# merger/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .viewsets import UserViewSet, current_user

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', obtain_auth_token, name='api-login'),  # Flet will POST here to get token
    path('me/', current_user, name='api-me'),            # Flet will GET here to get user info
]