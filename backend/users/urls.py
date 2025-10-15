# backend/users/urls.py
"""
ユーザー管理APIのURL設定

このファイルの役割:
- ユーザー管理のAPIエンドポイントを定義
- REST Framework の Router を使って自動的にURLを生成

生成されるURL:
- GET    /api/users/           → ユーザー一覧
- POST   /api/users/           → ユーザー作成
- GET    /api/users/{id}/      → ユーザー詳細
- PUT    /api/users/{id}/      → ユーザー更新
- PATCH  /api/users/{id}/      → ユーザー部分更新
- DELETE /api/users/{id}/      → ユーザー削除（論理削除）

カスタムアクション（追加URL）:
- POST   /api/users/bulk-delete/    → 一括削除
- POST   /api/users/{id}/restore/   → 復元
- POST   /api/users/bulk-restore/   → 一括復元
- GET    /api/users/deleted/        → 削除済み一覧
- GET    /api/users/stats/          → 統計情報
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

# ==================== 名前空間の設定 ====================
# 名前空間を使うと、他のアプリとURL名が重複しても区別できる
# 使い方: reverse('users:user-list')
app_name = 'users'

# ==================== Router の設定 ====================
# DefaultRouter = REST Framework が自動的にURLを生成してくれる
router = DefaultRouter()

# ViewSet を登録
# 第1引数: URL のプレフィックス（/api/users/）
# 第2引数: ViewSet クラス
# basename: URL の名前（user-list, user-detail など）
router.register(r'users', UserViewSet, basename='user')

# ==================== URL パターン ====================
urlpatterns = [
    # Router が生成したURLをすべて含める
    path('', include(router.urls)),
]


# ==================== 生成されるURL一覧 ====================
"""
Router が自動生成するURL:

[基本のCRUD]
GET     /api/users/              → user-list (一覧)
POST    /api/users/              → user-list (作成)
GET     /api/users/{id}/         → user-detail (詳細)
PUT     /api/users/{id}/         → user-detail (更新)
PATCH   /api/users/{id}/         → user-detail (部分更新)
DELETE  /api/users/{id}/         → user-detail (削除)

[カスタムアクション（views.py の @action で定義）]
POST    /api/users/bulk-delete/      → bulk-delete (一括削除)
POST    /api/users/{id}/restore/     → restore (復元)
POST    /api/users/bulk-restore/     → bulk-restore (一括復元)
GET     /api/users/deleted/          → deleted (削除済み一覧)
GET     /api/users/stats/            → stats (統計情報)


URLの名前（reverse で使用）:
- users:user-list          → /api/users/
- users:user-detail        → /api/users/{id}/
- users:user-bulk-delete   → /api/users/bulk-delete/
- users:user-restore       → /api/users/{id}/restore/
- users:user-bulk-restore  → /api/users/bulk-restore/
- users:user-deleted       → /api/users/deleted/
- users:user-stats         → /api/users/stats/
"""


# ==================== Router の仕組み ====================
"""
DefaultRouter の動作:

1. ModelViewSet を登録すると自動的に以下のアクションに対応:
   - list: GET /api/users/
   - create: POST /api/users/
   - retrieve: GET /api/users/{id}/
   - update: PUT /api/users/{id}/
   - partial_update: PATCH /api/users/{id}/
   - destroy: DELETE /api/users/{id}/

2. @action デコレータで追加したメソッドもURLに追加される:
   - detail=False: /api/users/{action_name}/
   - detail=True:  /api/users/{id}/{action_name}/

3. URL名は自動生成される:
   - basename を 'user' にすると:
     - user-list, user-detail, user-{action_name} という名前になる
"""


# ==================== カスタムURLの追加例 ====================
"""
Router以外のURLを追加したい場合:

urlpatterns = [
    path('', include(router.urls)),
    
    # カスタムURL（ViewSetではない通常のViewを使う場合）
    path('custom/', CustomAPIView.as_view(), name='custom'),
]
"""