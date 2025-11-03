"""
認証関連API
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

from .serializers import LoginSerializer, UserSerializer

audit_logger = logging.getLogger("audit")


class CSRFView(APIView):
    """CSRFトークン取得API"""

    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginAPIView(APIView):
    """ログインAPI(ブルートフォース攻撃対策)"""

    permission_classes = [AllowAny]

    @staticmethod
    def _get_cache_key(employee_id):
        return f"login_attempts:{employee_id}"

    @staticmethod
    def _get_lockout_key(employee_id):
        return f"login_locked:{employee_id}"

    def _increment_attempts(self, employee_id):
        """ログイン失敗回数をインクリメント"""
        key = self._get_cache_key(employee_id)
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, 3600)
        return attempts

    def _is_locked(self, employee_id):
        """アカウントがロック中か確認"""
        return cache.get(self._get_lockout_key(employee_id), False)

    def _lock_user(self, employee_id):
        """アカウントをロック"""
        key = self._get_lockout_key(employee_id)
        cache.set(key, True, settings.LOGIN_LOCKOUT_DURATION)

    def _reset_attempts(self, employee_id):
        """ログイン失敗回数をリセット"""
        cache.delete(self._get_cache_key(employee_id))
        cache.delete(self._get_lockout_key(employee_id))

    def post(self, request):
        """ログイン処理"""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        employee_id = serializer.validated_data["employee_id"]
        password = serializer.validated_data["password"]

        # ロックチェック
        if self._is_locked(employee_id):
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

        # 認証
        user = authenticate(request, username=employee_id, password=password)

        if user:
            if not user.is_active:
                self._increment_attempts(employee_id)
                return Response(
                    {"detail": str(_("社員番号またはパスワードが正しくありません"))},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # ログイン成功
            self._reset_attempts(employee_id)
            login(request, user)

            return Response(
                {
                    "detail": "logged_in",
                    "user": UserSerializer(user).data,
                }
            )

        # 認証失敗
        attempts = self._increment_attempts(employee_id)

        if attempts >= settings.LOGIN_MAX_ATTEMPTS:
            self._lock_user(employee_id)
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
            {"detail": str(_("社員番号またはパスワードが正しくありません"))},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutAPIView(APIView):
    """ログアウトAPI"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        ログアウト処理

        Note:
            logout()実行前にユーザー情報を保存して監査ログに記録
        """
        # ログアウト前にユーザー情報を保存
        user_info = request.user.employee_id
        request_id = getattr(request, "_request_id", "N/A")
        ip = get_client_ip(request)

        # ログアウト実行
        logout(request)

        # 監査ログに記録
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
            },
        )

        return Response({"detail": "logged_out"})


class MeAPIView(APIView):
    """現在のユーザー情報取得API"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
