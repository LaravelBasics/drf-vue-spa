"""
カスタムミドルウェア

Django公式推奨のモダンスタイルに準拠
"""

import logging
import json
import uuid
from django.utils.translation import activate
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
            'fr,de' → None(未対応)
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


class AuditMiddleware:
    """
    API監査ミドルウェア

    ログイン・ログアウトを監査ログに記録
    リクエストIDを管理(X-Request-ID or UUID生成)

    Note:
        モデルの作成/更新/削除はシグナルで自動記録されるため
        ここでは認証関連のみ記録
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """リクエスト処理"""
        # リクエストIDを取得 or 生成
        request_id = request.META.get("HTTP_X_REQUEST_ID", str(uuid.uuid4()))
        request._request_id = request_id

        # リクエストをスレッドローカルに保存(シグナルで使用)
        set_current_request(request)

        # レスポンス取得
        response = self.get_response(request)

        # レスポンスヘッダーにリクエストIDを追加
        response["X-Request-ID"] = request_id

        # 監査ログ記録
        self._log_auth_events(request, response)

        return response

    def _log_auth_events(self, request, response):
        """
        認証関連イベントのログ記録

        Args:
            request: HTTPリクエスト
            response: HTTPレスポンス

        Note:
            ログアウトはView内で記録されるため、ここではログインのみ記録
        """
        # ログアウトはView内で記録済みなのでスキップ
        if request.path == "/api/auth/logout/":
            return

        # 基本情報(DRY原則)
        user_info = (
            request.user.employee_id
            if hasattr(request, "user") and request.user.is_authenticated
            else "anonymous"
        )

        base_extra = {
            "request_id": getattr(request, "_request_id", "N/A"),
            "user": user_info,
            "model": "Auth",
            "object_id": None,
            "ip": get_client_ip(request),
        }

        # ログインのみ記録
        if request.path == "/api/auth/login/":
            if response.status_code == 200:
                audit_logger.info(
                    "ユーザーがログインしました",
                    extra={**base_extra, "action": "LOGIN", "changes": "{}"},
                )
            else:
                audit_logger.warning(
                    f"ログイン失敗(status: {response.status_code})",
                    extra={
                        **base_extra,
                        "action": "LOGIN_FAILED",
                        "changes": json.dumps({"status_code": response.status_code}),
                    },
                )
