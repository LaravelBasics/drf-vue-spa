# backend/accounts/urls.py
"""
認証API のURL設定

このファイルの役割:
- ログイン・ログアウト・ユーザー情報取得のエンドポイントを定義
"""

from django.urls import path
from .views import LoginAPIView, LogoutAPIView, MeAPIView, CSRFView

# 名前空間を設定（他のアプリとURL名が重複しても区別できる）
app_name = 'accounts'

urlpatterns = [
    # ==================== CSRF トークン取得 ====================
    # URL: /api/auth/csrf/
    # メソッド: GET
    # 権限: AllowAny（誰でもアクセスOK）
    # 用途: ログイン前にCSRFトークンを取得
    path('csrf/', CSRFView.as_view(), name='csrf'),
    
    # ==================== ログイン ====================
    # URL: /api/auth/login/
    # メソッド: POST
    # 権限: AllowAny
    # リクエストボディ:
    #   {
    #     "employee_id": "9999",
    #     "password": "test1234"
    #   }
    # レスポンス:
    #   {
    #     "detail": "logged_in",
    #     "user": { ユーザー情報 }
    #   }
    path('login/', LoginAPIView.as_view(), name='login'),
    
    # ==================== ログアウト ====================
    # URL: /api/auth/logout/
    # メソッド: POST
    # 権限: IsAuthenticated（ログイン済みのみ）
    # レスポンス:
    #   {
    #     "detail": "logged_out"
    #   }
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    
    # ==================== 現在のユーザー情報 ====================
    # URL: /api/auth/me/
    # メソッド: GET
    # 権限: IsAuthenticated
    # レスポンス:
    #   {
    #     "id": 1,
    #     "employee_id": "9999",
    #     "username": "管理者",
    #     "email": "admin@example.com",
    #     "is_admin": true
    #   }
    path('me/', MeAPIView.as_view(), name='me'),
]


# ==================== URL名の使い方 ====================
"""
Django テンプレートやコード内でURLを参照する場合:

# Python コード内
from django.urls import reverse
url = reverse('accounts:login')  # → '/api/auth/login/'
url = reverse('accounts:logout') # → '/api/auth/logout/'
url = reverse('accounts:me')     # → '/api/auth/me/'

# テンプレート内（このプロジェクトでは使わない）
{% url 'accounts:login' %}
"""