# backend/api/urls.py
from django.urls import path
from .views import login_api, logout_api, me_api, CSRFView

urlpatterns = [
    path('csrf/', CSRFView.as_view(), name='csrf'),
    path('login/', login_api, name='login'),
    path('logout/', logout_api, name='logout'),
    path('me/', me_api, name='me'),
]