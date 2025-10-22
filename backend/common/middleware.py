"""
カスタムミドルウェア
"""

import logging
import json
import uuid
from django.utils.translation import activate
from django.utils.deprecation import MiddlewareMixin
from common.context import set_current_request, get_client_ip

audit_logger = logging.getLogger("audit")


class LanguageMiddleware:
    """
    Accept-Language ヘッダーから言語を設定

    フロントエンドから送信されたヘッダーに基づいて
    Djangoの言語設定を動的に切り替える。

    Example:
        Accept-Language: ja,en-US;q=0.9 → 'ja' を設定
        Accept-Language: fr → デフォルト言語にフォールバック
    """

    # 対応言語
    SUPPORTED_LANGS = {"ja", "en"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")

        if accept_language:
            lang = self._parse_language(accept_language)
            if lang:
                activate(lang)

        return self.get_response(request)

    def _parse_language(self, accept_language):
        """
        Accept-Language ヘッダーをパースして対応言語コードを返す

        Args:
            accept_language: Accept-Language ヘッダーの値

        Returns:
            str: 対応言語コード or None

        Examples:
            'ja,en-US;q=0.9' → 'ja'
            'en-GB,en' → 'en'
            'fr,de' → None（未対応）
            'invalid;;data' → None
        """
        try:
            # 最初の言語を抽出: 'ja,en-US;q=0.9' → 'ja'
            lang = accept_language.split(",")[0].split("-")[0].strip().lower()

            # 対応言語のみ返す
            if lang in self.SUPPORTED_LANGS:
                return lang

        except (IndexError, AttributeError, ValueError):
            # 不正なヘッダーは無視
            pass

        return None


class AuditMiddleware(MiddlewareMixin):
    """
    API監査ミドルウェア

    ログイン・ログアウトを監査ログに記録
    リクエストIDを管理（X-Request-ID or UUID生成）

    Note:
        モデルの作成/更新/削除はシグナルで自動記録されるため
        ここでは認証関連のみ記録
    """

    def process_request(self, request):
        """リクエスト前処理"""
        # リクエストIDを取得 or 生成
        request_id = request.META.get("HTTP_X_REQUEST_ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        request._request_id = request_id

        # リクエストをスレッドローカルに保存（シグナルで使用）
        set_current_request(request)

        return None

    def process_response(self, request, response):
        """レスポンス後処理"""
        # レスポンスヘッダーにリクエストIDを追加
        if hasattr(request, "_request_id"):
            response["X-Request-ID"] = request._request_id

        # ユーザー情報取得
        user_info = "anonymous"
        if hasattr(request, "user") and request.user.is_authenticated:
            user_info = request.user.employee_id

        ip = get_client_ip(request)
        request_id = getattr(request, "_request_id", "N/A")

        # ログイン（成功・失敗）
        if request.path == "/api/auth/login/":
            if response.status_code == 200:
                audit_logger.info(
                    "ユーザーがログインしました",
                    extra={
                        "request_id": request_id,
                        "user": user_info,
                        "action": "LOGIN",
                        "model": "Auth",
                        "object_id": None,
                        "ip": ip,
                        "changes": "{}",
                    },
                )
            else:
                audit_logger.warning(
                    f"ログイン失敗（status: {response.status_code}）",
                    extra={
                        "request_id": request_id,
                        "user": user_info,
                        "action": "LOGIN_FAILED",
                        "model": "Auth",
                        "object_id": None,
                        "ip": ip,
                        "changes": json.dumps({"status_code": response.status_code}),
                    },
                )

        # ログアウト
        elif request.path == "/api/auth/logout/" and response.status_code == 200:
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

        return response
