"""
カスタムミドルウェア（Phase 1 拡張版）

追加情報:
- endpoint: リクエストURL
- http_method: HTTPメソッド（GET/POST/etc）
- http_status: レスポンスステータスコード
- object_repr: オブジェクトの人間が読める表現
- view_name: View関数/クラス名
"""

import logging
import json
import uuid
from django.utils.translation import activate
from django.urls import resolve
from common.context import set_current_request, get_client_ip

audit_logger = logging.getLogger("audit")


class LanguageMiddleware:
    """Accept-Language ヘッダーから言語を設定"""

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
        try:
            lang = accept_language.split(",")[0].split("-")[0].strip().lower()
            if lang in self.SUPPORTED_LANGS:
                return lang
        except (IndexError, AttributeError, ValueError):
            pass
        return None


class AuditMiddleware:
    """
    API監査ミドルウェア（Phase 1 拡張版）

    記録対象:
    - ログイン・ログアウト（認証イベント）
    - 機密情報の閲覧（GET + URLパターン判定）
    - リクエストIDの管理

    Phase 1 追加情報:
    - endpoint, http_method, http_status
    - object_repr, view_name
    """

    SENSITIVE_URL_PATTERNS = [
        "/api/users/",
        "/api/employees/",
        "/api/salaries/",
    ]

    EXCLUDE_PATHS = {
        "/admin/",
        "/static/",
        "/media/",
        "/health/",
        "/api/auth/csrf/",
        "/api/auth/me/",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """リクエスト処理"""
        request_id = request.META.get("HTTP_X_REQUEST_ID", str(uuid.uuid4()))
        request._request_id = request_id

        set_current_request(request)

        response = self.get_response(request)

        response["X-Request-ID"] = request_id

        self._log_audit_events(request, response)

        return response

    def _log_audit_events(self, request, response):
        """監査ログの記録"""
        if self._should_skip_audit(request):
            return

        if request.path == "/api/auth/login/":
            self._log_auth_event(request, response, "LOGIN")
            return

        if request.path == "/api/auth/logout/":
            return

        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return

        if request.method == "GET":
            self._log_sensitive_read(request, response)

    def _should_skip_audit(self, request):
        """監査をスキップすべきか判定"""
        return any(request.path.startswith(path) for path in self.EXCLUDE_PATHS)

    def _is_sensitive_url(self, path):
        """機密情報のURLかチェック"""
        return any(path.startswith(pattern) for pattern in self.SENSITIVE_URL_PATTERNS)

    def _extract_resource_id(self, path):
        """URLからリソースIDを抽出"""
        try:
            parts = [p for p in path.split("/") if p]
            if len(parts) >= 2 and parts[-1]:
                return parts[-1]
        except (IndexError, AttributeError):
            pass
        return None

    def _get_view_name(self, request):
        """
        View関数/クラス名を取得

        Examples:
            'UserDetailView' or 'user_detail_view'
        """
        try:
            resolver_match = resolve(request.path)
            view_func = resolver_match.func

            # クラスベースViewの場合
            if hasattr(view_func, "view_class"):
                return view_func.view_class.__name__

            # 関数ベースViewの場合
            if hasattr(view_func, "__name__"):
                return view_func.__name__

            # DRF ViewSetの場合
            if hasattr(view_func, "cls"):
                return view_func.cls.__name__

        except Exception:
            pass

        return "UnknownView"

    def _get_object_repr(self, request, resource_id):
        """
        オブジェクトの人間が読める表現を取得

        Examples:
            '山田花子（EMP0001）'
            'ユーザー EMP0001'
        """
        # モデルからオブジェクトを取得して __str__ を使う場合
        # （パフォーマンス考慮が必要）

        # 簡易版: リソースIDをそのまま使用
        if resource_id:
            model_name = self._guess_model_name(request.path)
            return f"{model_name} {resource_id}"

        return ""

    def _guess_model_name(self, path):
        """
        URLからモデル名を推測

        Examples:
            '/api/users/EMP001/' → 'User'
            '/api/employees/123/' → 'Employee'
        """
        try:
            parts = [p for p in path.split("/") if p]
            if len(parts) >= 2:
                # 'users' → 'User'
                model_name = parts[1].rstrip("s").capitalize()
                return model_name
        except (IndexError, AttributeError):
            pass

        return "Unknown"

    def _log_sensitive_read(self, request, response):
        """機密情報の閲覧を記録（GET）"""
        if not (hasattr(request, "user") and request.user.is_authenticated):
            return

        if response.status_code >= 400:
            return

        if not self._is_sensitive_url(request.path):
            return

        resource_id = self._extract_resource_id(request.path)
        if not resource_id:
            return

        user_info = request.user.user_id

        # ★Phase 1: 追加情報を収集★
        view_name = self._get_view_name(request)
        object_repr = self._get_object_repr(request, resource_id)

        audit_logger.warning(
            f"機密情報閲覧: {request.path} [ID: {resource_id}]",
            extra={
                # 既存項目
                "request_id": request._request_id,
                "user": user_info,
                "action": "READ_SENSITIVE",
                "model": self._guess_model_name(request.path),
                "object_id": resource_id,
                "ip": get_client_ip(request),
                # ★Phase 1: 追加項目★
                "endpoint": request.path,  # どのURL
                "http_method": request.method,  # どのHTTPメソッド
                "http_status": response.status_code,  # ステータスコード
                "object_repr": object_repr,  # オブジェクトの表現
                "view_name": view_name,  # View名
                "changes": json.dumps(
                    {
                        "path": request.path,
                        "query_params": dict(request.GET),
                    },
                    ensure_ascii=False,
                ),
            },
        )

    def _log_auth_event(self, request, response, action_type):
        """認証関連イベントのログ記録"""
        user_info = (
            request.user.user_id
            if hasattr(request, "user") and request.user.is_authenticated
            else "anonymous"
        )

        # ★Phase 1: 追加情報★
        view_name = self._get_view_name(request)

        base_extra = {
            "request_id": getattr(request, "_request_id", "N/A"),
            "user": user_info,
            "model": "Auth",
            "object_id": None,
            "ip": get_client_ip(request),
            # ★Phase 1: 追加項目★
            "endpoint": request.path,
            "http_method": request.method,
            "http_status": response.status_code,
            "view_name": view_name,
            "object_repr": "",
        }

        if response.status_code == 200:
            audit_logger.info(
                f"ユーザーが{'ログイン' if action_type == 'LOGIN' else 'ログアウト'}しました",
                extra={**base_extra, "action": action_type, "changes": "{}"},
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
