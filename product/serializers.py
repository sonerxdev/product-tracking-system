from rest_framework import serializers
from .models import User, Room, Product, Notification, RoomMember

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'company_id']

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'company', 'created_by', 'stages']

class ProductSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)  # Ürünü oluşturan kullanıcıyı görmek için
    room = RoomSerializer(read_only=True)  # Ürünün ait olduğu odayı görmek için
    class Meta:
        model = Product
        fields = ['id', 'name', 'code', 'quantity', 'price', 'photo', 'qr_code', 'current_stage', 'room', 'created_by']

class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Bildirimi alan kullanıcıyı görmek için
    room = RoomSerializer(read_only=True)  # Bildirime ait odayı görmek için
    class Meta:
        model = Notification
        fields = ['id', 'room', 'user', 'type', 'status', 'created_at']

class RoomMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomMember
        fields = ['id', 'user', 'room', 'role', 'status', 'created_at']
