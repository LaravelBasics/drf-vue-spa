"""
プロジェクト全体のURLルーティング

URL構造:
/admin/              → Django管理画面
/api/auth/*          → 認証API（accounts アプリ）
/api/users/*         → ユーザー管理API（users アプリ）
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django管理画面
    path('admin/', admin.site.urls),
    
    # 認証API
    path('api/auth/', include('accounts.urls')),
    
    # ユーザー管理API
    path('api/', include('users.urls')),
]