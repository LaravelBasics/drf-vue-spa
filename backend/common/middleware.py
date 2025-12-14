"""
カスタムミドルウェア

- endpoint: リクエストURL
- http_method: HTTPメソッド（GET/POST/etc）
- http_status: レスポンスステータスコード
- object_repr: オブジェクトの人間が読める表現
- view_name: View関数/クラス名

セキュリティ対策:
- ログインジェクション対策（改行文字の除去）
- 大量データ攻撃対策（長さ制限）
- 特殊文字のサニタイゼーション
"""

import logging
import json
import uuid
import re
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
    API監査ミドルウェア（Phase 1 拡張版 + セキュリティ強化）

    記録対象:
    - ログイン・ログアウト（認証イベント）
    - 機密情報の閲覧（GET + URLパターン判定）
    - リクエストIDの管理

    追加情報:
    - endpoint, http_method, http_status
    - object_repr, view_name

    セキュリティ対策:
    - user_id のサニタイゼーション（長さ制限、改行除去、特殊文字フィルタ）
    """

    # 記録したいGET
    SENSITIVE_URL_PATTERNS = [
        "/api/users/",
    ]

    # 記録したくないリクエスト
    EXCLUDE_PATHS = {
        "/api/auth/csrf/",
        "/api/auth/me/",
    }

    # ========================================
    # セキュリティ設定
    # ========================================
    MAX_USER_ID_LENGTH = 100  # user_idの最大長（LoginSerializerと同じ制限）
    SANITIZE_PATTERN = re.compile(r"[\x00-\x1f\x7f-\x9f]")  # 制御文字を除去

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """リクエスト処理"""
        request_id = request.META.get("HTTP_X_REQUEST_ID", str(uuid.uuid4()))
        request._request_id = request_id

        set_current_request(request)

        # View実行前にuser_idを取得
        if request.path == "/api/auth/login/" and request.method == "POST":
            self._extract_login_attempt_user_id(request)

        response = self.get_response(request)

        response["X-Request-ID"] = request_id

        self._log_audit_events(request, response)

        return response

    def _sanitize_user_id(self, user_id):
        """
        ★user_idのサニタイゼーション

        対策:
        1. 長さ制限（DoS対策）
        2. 改行文字の除去（ログインジェクション対策）
        3. 制御文字の除去（ログ破壊対策）
        4. 空文字・None対応

        Args:
            user_id: サニタイゼーション前のuser_id

        Returns:
            str: サニタイズ済みuser_id
        """
        if not user_id:
            return "empty_user_id"

        # 文字列に変換（万が一intなどが来た場合）
        user_id = str(user_id)

        # 1. 長さ制限（最大100文字、LoginSerializerと同じ）
        if len(user_id) > self.MAX_USER_ID_LENGTH:
            user_id = user_id[: self.MAX_USER_ID_LENGTH] + "...[truncated]"

        # 2. 改行文字の除去（ログインジェクション対策）
        user_id = user_id.replace("\n", "").replace("\r", "")

        # 3. 制御文字の除去（\x00-\x1f, \x7f-\x9f）
        user_id = self.SANITIZE_PATTERN.sub("", user_id)

        # 4. 前後の空白を除去
        user_id = user_id.strip()

        # 5. 最終チェック: 空文字になった場合
        if not user_id:
            return "empty_user_id"

        return user_id

    def _extract_login_attempt_user_id(self, request):
        """
        ログイン試行のuser_idを事前に取得（セキュリティ強化版）

        タイミング:
        - View実行前（CSRF検証前）
        - get_response() の前

        取得先:
        1. request.POST（通常のPOSTデータ）
        2. JSONボディ（Content-Type: application/json）

        セキュリティ:
        - 取得後に必ずサニタイゼーション実施
        """
        user_id = None

        # 1. 通常のPOSTデータから取得
        try:
            if hasattr(request, "POST") and request.POST:
                user_id = request.POST.get("user_id")
        except Exception:
            pass

        # 2. JSONボディから取得
        if not user_id:
            try:
                content_type = request.META.get("CONTENT_TYPE", "")
                if "application/json" in content_type and request.body:
                    data = json.loads(request.body.decode("utf-8"))
                    user_id = data.get("user_id")
            except Exception:
                pass

        # ★セキュリティ強化★ サニタイゼーション実施
        sanitized_user_id = self._sanitize_user_id(user_id)
        request._login_attempt_user_id = sanitized_user_id

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
        """View関数/クラス名を取得"""
        try:
            resolver_match = resolve(request.path)
            view_func = resolver_match.func

            if hasattr(view_func, "view_class"):
                return view_func.view_class.__name__
            if hasattr(view_func, "__name__"):
                return view_func.__name__
            if hasattr(view_func, "cls"):
                return view_func.cls.__name__
        except Exception:
            pass
        return "UnknownView"

    def _get_object_repr(self, request, resource_id):
        """オブジェクトの人間が読める表現を取得"""
        if resource_id:
            model_name = self._guess_model_name(request.path)
            return f"{model_name} {resource_id}"
        return ""

    def _guess_model_name(self, path):
        """URLからモデル名を推測"""
        try:
            parts = [p for p in path.split("/") if p]
            if len(parts) >= 2:
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
        view_name = self._get_view_name(request)
        object_repr = self._get_object_repr(request, resource_id)

        audit_logger.warning(
            f"機密情報閲覧: {request.path} [ID: {resource_id}]",
            extra={
                "request_id": request._request_id,
                "user": user_info,
                "action": "READ_SENSITIVE",
                "model": self._guess_model_name(request.path),
                "object_id": resource_id,
                "ip": get_client_ip(request),
                "endpoint": request.path,
                "http_method": request.method,
                "http_status": response.status_code,
                "object_repr": object_repr,
                "view_name": view_name,
                "changes": json.dumps(
                    {"path": request.path, "query_params": dict(request.GET)},
                    ensure_ascii=False,
                ),
            },
        )

    def _log_auth_event(self, request, response, action_type):
        """
        認証関連イベントのログ記録

        セキュリティ:
        - user_idは事前にサニタイズ済み
        """
        user_info = (
            request.user.user_id
            if hasattr(request, "user") and request.user.is_authenticated
            else "anonymous"
        )

        # ログイン試行時は、View実行前に取得した（サニタイズ済み）user_idを使用
        if action_type == "LOGIN" and hasattr(request, "_login_attempt_user_id"):
            user_info = request._login_attempt_user_id

        view_name = self._get_view_name(request)

        base_extra = {
            "request_id": getattr(request, "_request_id", "N/A"),
            "user": user_info,
            "model": "Auth",
            "object_id": None,
            "ip": get_client_ip(request),
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
