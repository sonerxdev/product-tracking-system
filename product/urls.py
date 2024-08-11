# product/urls.py

from django.urls import path
from .views import register_user, login_user, create_room, list_rooms, room_detail, add_product, product_detail, list_notifications

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('rooms/', list_rooms, name='list_rooms'),
    path('rooms/create/', create_room, name='create_room'),
    path('rooms/<int:room_id>/', room_detail, name='room_detail'),
    path('rooms/<int:room_id>/add_product/', add_product, name='add_product'),
    path('products/<int:product_id>/', product_detail, name='product_detail'),
    path('notifications/', list_notifications, name='list_notifications'),
]