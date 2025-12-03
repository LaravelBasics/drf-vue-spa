from django.contrib import admin
from django.urls import path, include

# from django.conf import settings  # 検証ツール、本番NG

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("users.urls")),
]

# Debug Toolbar用（最後に追加）
# if settings.DEBUG:
#     import debug_toolbar

#     urlpatterns = [
#         path("__debug__/", include(debug_toolbar.urls)),
#     ] + urlpatterns
