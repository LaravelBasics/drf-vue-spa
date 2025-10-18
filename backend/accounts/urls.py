"""
認証API のURLルーティング

エンドポイント:
- GET  /api/auth/csrf/   → CSRF トークン取得
- POST /api/auth/login/  → ログイン
- POST /api/auth/logout/ → ログアウト
- GET  /api/auth/me/     → 現在のユーザー情報
"""

from django.urls import path
from .views import LoginAPIView, LogoutAPIView, MeAPIView, CSRFView

app_name = 'accounts'

urlpatterns = [
    # CSRF トークン取得（ログイン前に必要）
    path('csrf/', CSRFView.as_view(), name='csrf'),
    
    # ログイン（社員番号 + パスワード）
    path('login/', LoginAPIView.as_view(), name='login'),
    
    # ログアウト
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    
    # 現在のユーザー情報
    path('me/', MeAPIView.as_view(), name='me'),
]