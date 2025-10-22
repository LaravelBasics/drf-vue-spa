"""
監査ログ用コンテキスト管理

シグナル内でリクエスト情報にアクセスするためのヘルパー関数。
スレッドローカルストレージを使用して、リクエストを安全に共有。
"""

import threading

# スレッドローカルストレージ
_request_local = threading.local()


def set_current_request(request):
    """
    現在のリクエストをスレッドローカルに保存

    Args:
        request: Django HTTPRequest オブジェクト

    Note:
        ミドルウェアの process_request() で呼び出される
    """
    _request_local.request = request


def get_current_request():
    """
    現在のリクエストをスレッドローカルから取得

    Returns:
        HTTPRequest or None: リクエストオブジェクト

    Note:
        シグナル内で呼び出される
    """
    return getattr(_request_local, "request", None)


def get_client_ip(request):
    """
    クライアントのIPアドレスを取得

    Args:
        request: Django HTTPRequest オブジェクト

    Returns:
        str: IPアドレス

    Note:
        プロキシ経由の場合は X-Forwarded-For ヘッダーを優先
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        # プロキシ経由の場合、最初のIPを取得
        return x_forwarded_for.split(",")[0].strip()

    # 直接接続の場合
    return request.META.get("REMOTE_ADDR", "127.0.0.1")
