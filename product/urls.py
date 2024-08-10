# core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CompanyViewSet, RoomViewSet, RoomMemberViewSet, ProductViewSet, NotificationViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'room-members', RoomMemberViewSet)
router.register(r'products', ProductViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]