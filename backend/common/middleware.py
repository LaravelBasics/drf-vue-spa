"""
カスタムミドルウェア
"""

import logging
import json
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

    ログイン・ログアウト・API操作を監査ログに記録
    """

    def process_request(self, request):
        """リクエスト前処理"""
        # リクエストをスレッドローカルに保存（シグナルで使用）
        set_current_request(request)

        # リクエスト情報を保存
        request._audit_data = {
            "method": request.method,
            "path": request.path,
        }

        return None

    def process_response(self, request, response):
        """レスポンス後処理"""
        # ユーザー情報取得
        user_info = "anonymous"
        if hasattr(request, "user") and request.user.is_authenticated:
            user_info = request.user.employee_id

        ip = get_client_ip(request)

        # ログイン成功
        if request.path == "/api/auth/login/" and response.status_code == 200:
            audit_logger.info(
                "ユーザーがログインしました",
                extra={
                    "user": user_info,
                    "action": "LOGIN",
                    "model": "Auth",
                    "object_id": None,
                    "ip": ip,
                    "changes": "{}",
                },
            )

        # ログアウト
        elif request.path == "/api/auth/logout/" and response.status_code == 200:
            audit_logger.info(
                "ユーザーがログアウトしました",
                extra={
                    "user": user_info,
                    "action": "LOGOUT",
                    "model": "Auth",
                    "object_id": None,
                    "ip": ip,
                    "changes": "{}",
                },
            )

        # API操作（POST/PUT/PATCH/DELETE）
        elif request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            # /api/users/ 配下のみ記録
            if request.path.startswith("/api/users/"):
                action_map = {
                    "POST": "CREATE",
                    "PUT": "UPDATE",
                    "PATCH": "UPDATE",
                    "DELETE": "DELETE",
                }

                audit_logger.info(
                    f"{request.method} {request.path}",
                    extra={
                        "user": user_info,
                        "action": action_map[request.method],
                        "model": "User",
                        "object_id": None,
                        "ip": ip,
                        "changes": json.dumps({"status_code": response.status_code}),
                    },
                )

        return response
