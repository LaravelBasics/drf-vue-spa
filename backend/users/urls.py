"""
ユーザー管理URL設定

生成されるエンドポイント:
- GET/POST    /api/users/
- GET/PUT/PATCH/DELETE /api/users/{id}/
- POST  /api/users/bulk-delete/
- POST  /api/users/{id}/restore/
- POST  /api/users/bulk-restore/
- GET   /api/users/deleted/
- GET   /api/users/stats/
- GET   /api/users/admin-count/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

app_name = "users"

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
