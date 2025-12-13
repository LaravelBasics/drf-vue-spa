# accounts/views.py
"""
レガシーシステム対応 認証API

特徴:
- グループID + ユーザーID + パスワード認証
- ブルートフォース攻撃対策
- CSRF保護
- サービスクラスに処理を分離
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from rest_framework.authentication import SessionAuthentication

from .serializers import LoginSerializer, UserSerializer, GroupSerializer
from .services import LoginAttemptService, GroupService, UserGroupService

audit_logger = logging.getLogger("audit")


# ========================================
# カスタム認証クラス
# ========================================


class CSRFEnforcedSessionAuthentication(SessionAuthentication):
    """
    CSRF保護を強制するSessionAuthentication

    レガシーシステムでも標準のSessionAuthenticationを使用可能
    """

    def authenticate(self, request):
        """
        認証処理

        1. CSRF保護を強制
        2. セッションベース認証を実行
        """
        self.enforce_csrf(request)
        return super().authenticate(request)


# ========================================
# 認証API
# ========================================


class CSRFView(APIView):
    """
    CSRFトークン取得API

    フロントエンドがCSRFトークンを取得するためのエンドポイント
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        """CSRFトークンをCookieにセット"""
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupListAPIView(APIView):
    """
    グループ一覧取得API（ログイン画面用）

    用途:
    - ログイン画面のグループ選択プルダウン
    - 認証不要（AllowAny）
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        """アクティブなグループ一覧を返す"""
        groups = GroupService.get_active_groups()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)


class LoginAPIView(APIView):
    """
    グループ認証対応ログインAPI

    認証方式:
    - グループID + ユーザーID + パスワード の3点認証

    セキュリティ:
    - ブルートフォース攻撃対策（試行回数制限）
    - アカウントロック機能
    - タイミング攻撃対策（バックエンド側で実装）
    """

    permission_classes = [AllowAny]
    authentication_classes = [CSRFEnforcedSessionAuthentication]

    def post(self, request):
        """ログイン処理"""
        # ========================================
        # 1. バリデーション
        # ========================================
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = serializer.validated_data["user_id"]
        password = serializer.validated_data["password"]
        group_id = serializer.validated_data["group_id"]

        # ========================================
        # 2. アカウントロックチェック
        # ========================================
        if LoginAttemptService.is_locked(user_id, group_id):
            return Response(
                {
                    "detail": str(
                        _(
                            "ログイン試行が%(max_attempts)d回失敗しました。"
                            "%(lockout_duration)d秒後に再度お試しください"
                        )
                        % {
                            "max_attempts": settings.LOGIN_MAX_ATTEMPTS,
                            "lockout_duration": settings.LOGIN_LOCKOUT_DURATION,
                        }
                    )
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # ========================================
        # 3. 認証（グループ認証バックエンド使用）
        # ========================================
        user = authenticate(
            request=request,
            username=user_id,  # ← Django規約でパラメータ名はusername
            password=password,
            group_id=group_id,
        )

        # ========================================
        # 4. 認証結果処理
        # ========================================
        if user is not None:
            # --- 4-1. アクティブチェック ---
            if not user.is_active:
                LoginAttemptService.increment_attempts(user_id, group_id)
                return Response(
                    {"detail": str(_("ユーザーIDまたはパスワードが正しくありません"))},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # --- 4-2. ログイン成功 ---
            LoginAttemptService.reset_attempts(user_id, group_id)
            login(request, user)

            # セッションにグループIDを保存
            request.session["current_group_id"] = group_id

            # 監査ログ
            self._log_success(request, user_id, group_id)

            return Response(
                {
                    "detail": "logged_in",
                    "user": UserSerializer(user, context={"request": request}).data,
                }
            )

        # ========================================
        # 5. 認証失敗処理
        # ========================================
        attempts = LoginAttemptService.increment_attempts(user_id, group_id)

        # ロック判定
        if LoginAttemptService.should_lock(user_id, group_id):
            LoginAttemptService.lock_user(user_id, group_id)

            # 監査ログ
            self._log_lockout(request, user_id, group_id)

            return Response(
                {
                    "detail": str(
                        _(
                            "ログイン試行が%(max_attempts)d回失敗しました。"
                            "%(lockout_duration)d秒後に再度お試しください"
                        )
                        % {
                            "max_attempts": settings.LOGIN_MAX_ATTEMPTS,
                            "lockout_duration": settings.LOGIN_LOCKOUT_DURATION,
                        }
                    )
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # 監査ログ
        self._log_failure(request, user_id, group_id, attempts)

        return Response(
            {"detail": str(_("ユーザーIDまたはパスワードが正しくありません"))},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # ========================================
    # 監査ログ用ヘルパーメソッド
    # ========================================

    def _log_success(self, request, user_id, group_id):
        """ログイン成功ログ"""
        audit_logger.info(
            f"ログイン成功: user_id={user_id}, group_id={group_id}",
            extra={
                "action": "LOGIN_SUCCESS",
                "user_id": user_id,
                "group_id": group_id,
                "ip": self._get_client_ip(request),
            },
        )

    def _log_failure(self, request, user_id, group_id, attempts):
        """ログイン失敗ログ"""
        audit_logger.warning(
            f"ログイン失敗: user_id={user_id}, group_id={group_id}, attempts={attempts}",
            extra={
                "action": "LOGIN_FAILURE",
                "user_id": user_id,
                "group_id": group_id,
                "attempts": attempts,
                "ip": self._get_client_ip(request),
            },
        )

    def _log_lockout(self, request, user_id, group_id):
        """アカウントロックログ"""
        audit_logger.error(
            f"アカウントロック: user_id={user_id}, group_id={group_id}",
            extra={
                "action": "ACCOUNT_LOCKED",
                "user_id": user_id,
                "group_id": group_id,
                "ip": self._get_client_ip(request),
            },
        )

    @staticmethod
    def _get_client_ip(request):
        """クライアントIPアドレス取得"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")


class LogoutAPIView(APIView):
    """
    ログアウトAPI

    機能:
    - セッション破棄
    - 監査ログ記録
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [CSRFEnforcedSessionAuthentication]

    def post(self, request):
        """ログアウト処理"""
        user_id = request.user.user_id

        # print(user_id + " is logging out.")

        # 監査ログ
        audit_logger.info(
            "ユーザーがログアウトしました",
            extra={
                # "request_id": request_id,
                "user_id": user_id,
                "action": "LOGOUT",
                "model": "Auth",
                "object_id": None,
                "ip": self._get_client_ip(request),
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

        # セッション破棄
        logout(request)

        return Response({"detail": "logged_out"})

    @staticmethod
    def _get_client_ip(request):
        """クライアントIPアドレス取得"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")


class MeAPIView(APIView):
    """
    現在のユーザー情報取得API

    用途:
    - ページリロード時のユーザー情報復元
    - セッション有効性確認
    - グループ情報取得
    - 管理者権限確認（is_admin）
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [CSRFEnforcedSessionAuthentication]

    def get(self, request):
        """現在のログインユーザー情報を返す"""
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)
