# accounts/urls.py - グループ認証対応

from django.urls import path
from .views import (
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    CSRFView,
    GroupListAPIView,  # ← 追加
)

app_name = "accounts"

urlpatterns = [
    path("csrf/", CSRFView.as_view(), name="csrf"),
    path("groups/", GroupListAPIView.as_view(), name="groups"),  # ← 追加
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("me/", MeAPIView.as_view(), name="me"),
]
