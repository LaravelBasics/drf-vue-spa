# 2. backend/audit/middleware.py
# ============================================
import uuid
import threading

# スレッドローカルストレージ（リクエストごとに独立した変数を保存）
_thread_locals = threading.local()


def get_current_request():
    """現在のリクエストを取得"""
    return getattr(_thread_locals, 'request', None)


def get_current_request_id():
    """現在のリクエストIDを取得"""
    return getattr(_thread_locals, 'request_id', None)


class RequestIDMiddleware:
    """
    リクエストIDを管理するミドルウェア
    
    機能:
    - X-Request-ID ヘッダーがあればそれを使用
    - なければ UUID を自動生成
    - スレッドローカルストレージに保存してどこからでもアクセス可能に
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # X-Request-ID を取得（なければ UUID 生成）
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        request.request_id = request_id
        
        # スレッドローカルに保存
        _thread_locals.request = request
        _thread_locals.request_id = request_id
        
        # レスポンスヘッダーにも追加
        response = self.get_response(request)
        response['X-Request-ID'] = request_id
        
        return response