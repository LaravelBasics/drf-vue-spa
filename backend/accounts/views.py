"""
認証関連API

ログイン/ログアウト/ユーザー情報取得のエンドポイントを提供。
ブルートフォース攻撃対策を実装。
"""

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

from .serializers import LoginSerializer
from common.mixins import ErrorResponseMixin


class CSRFView(APIView):
    """CSRFトークン取得API"""

    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginAPIView(ErrorResponseMixin, APIView):
    """
    ログインAPI

    Features:
    - 社員番号とパスワードで認証
    - ブルートフォース攻撃対策（失敗回数制限）
    - 削除済み・無効化ユーザーのチェック
    """

    permission_classes = [AllowAny]

    MAX_LOGIN_ATTEMPTS = settings.LOGIN_MAX_ATTEMPTS
    LOCKOUT_DURATION = settings.LOGIN_LOCKOUT_DURATION
    CACHE_KEY_PREFIX = "login_attempts"
    LOCKOUT_KEY_PREFIX = "login_locked"

    def _get_cache_key(self, employee_id):
        return f"{self.CACHE_KEY_PREFIX}:{employee_id}"

    def _get_lockout_key(self, employee_id):
        return f"{self.LOCKOUT_KEY_PREFIX}:{employee_id}"

    def _increment_attempts(self, employee_id):
        """ログイン失敗回数をインクリメント"""
        cache_key = self._get_cache_key(employee_id)
        attempts = cache.get(cache_key, 0)
        attempts += 1
        cache.set(cache_key, attempts, 3600)
        return attempts

    def _is_locked(self, employee_id):
        """アカウントがロック中か確認"""
        lockout_key = self._get_lockout_key(employee_id)
        return cache.get(lockout_key, False)

    def _lock_user(self, employee_id):
        """アカウントをロック"""
        lockout_key = self._get_lockout_key(employee_id)
        cache.set(lockout_key, True, self.LOCKOUT_DURATION)

    def _reset_attempts(self, employee_id):
        """ログイン失敗回数をリセット"""
        cache.delete(self._get_cache_key(employee_id))
        cache.delete(self._get_lockout_key(employee_id))

    def post(self, request):
        """ログイン処理"""

        # バリデーション
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        employee_id = serializer.validated_data["employee_id"]
        password = serializer.validated_data["password"]

        # ロックチェック
        if self._is_locked(employee_id):
            return self.error_response(
                error_code="ACCOUNT_LOCKED",
                detail=str(
                    _(
                        "ログイン試行が%(max_attempts)d回失敗しました。%(lockout_duration)d秒後に再度お試しください"
                    )
                    % {
                        "max_attempts": self.MAX_LOGIN_ATTEMPTS,
                        "lockout_duration": self.LOCKOUT_DURATION,
                    }
                ),
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # 認証
        user = authenticate(request, username=employee_id, password=password)

        if user:
            # 無効化チェック
            if not user.is_active:
                self._increment_attempts(employee_id)
                return self.error_response(
                    error_code="ACCOUNT_INACTIVE",
                    detail=str(_("このアカウントは無効化されています")),
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            # ログイン成功
            self._reset_attempts(employee_id)
            login(request, user)

            return Response(
                {
                    "detail": "logged_in",
                    "user": {
                        "id": user.id,
                        "employee_id": user.employee_id,
                        "username": user.username,
                        "email": user.email,
                        "display_name": user.display_name,
                        "is_admin": user.is_admin,
                    },
                }
            )

        # 認証失敗
        attempts = self._increment_attempts(employee_id)

        # 上限到達でロック
        if attempts >= self.MAX_LOGIN_ATTEMPTS:
            self._lock_user(employee_id)
            return self.error_response(
                error_code="ACCOUNT_LOCKED",
                detail=str(
                    _(
                        "ログイン試行が%(max_attempts)d回失敗しました。%(lockout_duration)d秒後に再度お試しください"
                    )
                    % {
                        "max_attempts": self.MAX_LOGIN_ATTEMPTS,
                        "lockout_duration": self.LOCKOUT_DURATION,
                    }
                ),
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        return self.error_response(
            error_code="INVALID_CREDENTIALS",
            detail=str(_("社員番号またはパスワードが正しくありません")),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutAPIView(ErrorResponseMixin, APIView):
    """ログアウトAPI"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            logout(request)
            return Response({"detail": "logged_out"})
        except Exception:
            return self.error_response(
                error_code="LOGOUT_FAILED",
                detail=str(_("ログアウトに失敗しました")),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MeAPIView(APIView):
    """現在のユーザー情報取得API"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "employee_id": user.employee_id,
                "username": user.username,
                "email": user.email,
                "display_name": user.display_name,
                "is_admin": user.is_admin,
                "is_active": user.is_active,
            }
        )
