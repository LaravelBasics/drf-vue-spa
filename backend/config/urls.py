# backend/config/urls.py
"""
プロジェクト全体のURL設定

このファイルの役割:
- Django プロジェクト全体のURLルーティングを定義
- 各アプリのURLをまとめる

URL の構造:
/admin/              → Django管理画面
/api/auth/csrf/      → CSRF トークン取得
/api/auth/login/     → ログイン
/api/auth/logout/    → ログアウト
/api/auth/me/        → 現在のユーザー情報
/api/users/          → ユーザー一覧
/api/users/{id}/     → ユーザー詳細
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # ==================== Django管理画面 ====================
    # URL: http://localhost:8000/admin/
    # 用途: スーパーユーザーのみアクセス可能な管理画面
    path('admin/', admin.site.urls),
    
    # ==================== 認証API ====================
    # URL: http://localhost:8000/api/auth/
    # 接続先: accounts/urls.py
    # エンドポイント:
    #   - /api/auth/csrf/   → CSRFトークン取得
    #   - /api/auth/login/  → ログイン
    #   - /api/auth/logout/ → ログアウト
    #   - /api/auth/me/     → 現在のユーザー情報
    path('api/auth/', include('accounts.urls')),
    
    # ==================== ユーザー管理API ====================
    # URL: http://localhost:8000/api/
    # 接続先: users/urls.py
    # エンドポイント:
    #   - /api/users/                  → ユーザー一覧
    #   - /api/users/{id}/             → ユーザー詳細
    #   - /api/users/bulk-delete/      → 一括削除
    #   - /api/users/{id}/restore/     → 復元
    #   - /api/users/bulk-restore/     → 一括復元
    #   - /api/users/deleted/          → 削除済み一覧
    #   - /api/users/stats/            → 統計情報
    path('api/', include('users.urls')),
]


# ==================== URL設計のポイント ====================
"""
REST API の URL 設計:

【良い例】
GET    /api/users/              # ユーザー一覧
POST   /api/users/              # ユーザー作成
GET    /api/users/1/            # ユーザー詳細
PUT    /api/users/1/            # ユーザー更新
DELETE /api/users/1/            # ユーザー削除

【悪い例】
GET    /api/get-users/          # 動詞を入れない
POST   /api/create-user/        # 動詞を入れない
GET    /api/user?id=1           # クエリではなくパスで指定


【カスタムアクション】
POST   /api/users/bulk-delete/     # 複数形 + ハイフン
POST   /api/users/1/restore/       # 単数形 + ハイフン


【クエリパラメータ】
?page=2                  # ページング
?page_size=20            # ページサイズ
?search=山田             # 検索
?is_admin=true           # フィルター
?ordering=-created_at    # 並び替え
"""