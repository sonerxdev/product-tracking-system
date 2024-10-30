# product/urls.py

from django.urls import path
from .views import is_registered, register_user, create_room, list_rooms, room_detail, add_product, product_detail, list_notifications
from . import views

urlpatterns = [
    path('is_registered/', is_registered, name='is_registered'),
    path('register/', register_user, name='register'),
    path('rooms/', list_rooms, name='list_rooms'),
    path('rooms/create/', create_room, name='create_room'),
    path('rooms/<int:room_id>/', room_detail, name='room_detail'),
    path('rooms/<int:room_id>/add_product/', add_product, name='add_product'),
    path('products/<int:product_id>/', product_detail, name='product_detail'),
    path('notifications/', list_notifications, name='list_notifications'),
    path('home/', views.home_page, name='home_page'),
    path('token/refresh/', views.refresh_token, name='token_refresh'),
    path('users/update/', views.update_user_info, name='update_user_info')
]