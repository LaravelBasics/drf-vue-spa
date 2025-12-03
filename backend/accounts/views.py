"""
グループ認証対応 ログインAPI

グループID + ユーザーID + パスワード の3点セットで認証
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from common.context import get_client_ip
from rest_framework.authentication import SessionAuthentication

from .serializers import LoginSerializer, UserSerializer, GroupSerializer

audit_logger = logging.getLogger("audit")


# ===== Authentication =====


class CSRFEnforcedSessionAuthentication(SessionAuthentication):
    """CSRF保護を強制するSessionAuthentication"""

    def authenticate(self, request):
        self.enforce_csrf(request)
        return super().authenticate(request)


# ===== Views =====


class CSRFView(APIView):
    """CSRFトークン取得API"""

    permission_classes = [AllowAny]
    authentication_classes = []

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupListAPIView(APIView):
    """
    グループ一覧取得API（ログイン画面のプルダウン用）

    Note:
        認証不要。アクティブなグループのみ返す。
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        from users.models import Group

        groups = Group.objects.filter(is_active=True).order_by("group_id")
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)


class LoginAPIView(APIView):
    """
    グループ認証対応ログインAPI

    認証方式: グループID + ユーザーID + パスワード
    """

    permission_classes = [AllowAny]
    authentication_classes = [CSRFEnforcedSessionAuthentication]

    @staticmethod
    def _get_cache_key(user_id, group_id):
        """キャッシュキーを生成（グループIDも含める）"""
        return f"login_attempts:{group_id}:{user_id}"

    @staticmethod
    def _get_lockout_key(user_id, group_id):
        """ロックキーを生成"""
        return f"login_locked:{group_id}:{user_id}"

    def _increment_attempts(self, user_id, group_id):
        """ログイン失敗回数をインクリメント"""
        key = self._get_cache_key(user_id, group_id)
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, 3600)
        return attempts

    def _is_locked(self, user_id, group_id):
        """アカウントがロック中か確認"""
        return cache.get(self._get_lockout_key(user_id, group_id), False)

    def _lock_user(self, user_id, group_id):
        """アカウントをロック"""
        key = self._get_lockout_key(user_id, group_id)
        cache.set(key, True, settings.LOGIN_LOCKOUT_DURATION)

    def _reset_attempts(self, user_id, group_id):
        """ログイン失敗回数をリセット"""
        cache.delete(self._get_cache_key(user_id, group_id))
        cache.delete(self._get_lockout_key(user_id, group_id))

    def post(self, request):
        """グループ認証ログイン処理"""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = serializer.validated_data["user_id"]
        password = serializer.validated_data["password"]
        group_id = serializer.validated_data["group_id"]

        # ロックチェック
        if self._is_locked(user_id, group_id):
            return Response(
                {
                    "detail": str(
                        _(
                            "ログイン試行が%(max_attempts)d回失敗しました。%(lockout_duration)d秒後に再度お試しください"
                        )
                        % {
                            "max_attempts": settings.LOGIN_MAX_ATTEMPTS,
                            "lockout_duration": settings.LOGIN_LOCKOUT_DURATION,
                        }
                    )
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # 認証（グループIDも渡す）
        # Note: usernameパラメータ名はDjango規約だが、値はuser_id（プライマリキー）
        user = authenticate(
            request, username=user_id, password=password, group_id=group_id
        )

        if user:
            if not user.is_active:
                self._increment_attempts(user_id, group_id)
                return Response(
                    {"detail": str(_("ユーザーIDまたはパスワードが正しくありません"))},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # ログイン成功
            self._reset_attempts(user_id, group_id)
            login(request, user)

            # セッションにグループIDを保存（オプション）
            request.session["current_group_id"] = group_id

            return Response(
                {
                    "detail": "logged_in",
                    "user": UserSerializer(user).data,
                }
            )

        # 認証失敗
        attempts = self._increment_attempts(user_id, group_id)

        if attempts >= settings.LOGIN_MAX_ATTEMPTS:
            self._lock_user(user_id, group_id)
            return Response(
                {
                    "detail": str(
                        _(
                            "ログイン試行が%(max_attempts)d回失敗しました。%(lockout_duration)d秒後に再度お試しください"
                        )
                        % {
                            "max_attempts": settings.LOGIN_MAX_ATTEMPTS,
                            "lockout_duration": settings.LOGIN_LOCKOUT_DURATION,
                        }
                    )
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        return Response(
            {"detail": str(_("ユーザーIDまたはパスワードが正しくありません"))},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutAPIView(APIView):
    """ログアウトAPI"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [CSRFEnforcedSessionAuthentication]

    def post(self, request):
        user_info = request.user.user_id
        request_id = getattr(request, "_request_id", "N/A")
        ip = get_client_ip(request)

        logout(request)

        audit_logger.info(
            "ユーザーがログアウトしました",
            extra={
                "request_id": request_id,
                "user": user_info,
                "action": "LOGOUT",
                "model": "Auth",
                "object_id": None,
                "ip": ip,
                "changes": "{}",
                "endpoint": request.path,
                "http_method": request.method,
                "http_referer": request.META.get(
                    "HTTP_REFERER", ""
                ),  # リファラーもここで取得
                "http_status": 200,  # ログアウト成功は200を想定
                "view_name": self.__class__.__name__,
            },
        )

        return Response({"detail": "logged_out"})


class MeAPIView(APIView):
    """現在のユーザー情報取得API（グループ情報含む）"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # contextにrequestを渡す（これでSerializerがセッション情報にアクセス可能）
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)
