from django.urls import path
from .views import LoginAPIView, LogoutAPIView, MeAPIView, CSRFView

app_name = 'accounts'  # 名前空間を追加

urlpatterns = [
    path('csrf/', CSRFView.as_view(), name='csrf'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('me/', MeAPIView.as_view(), name='me'),
]