# core/serializers.py

from rest_framework import serializers
from .models import User, Company, Room, RoomMember, Product, Notification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'phone_number', 'company_id']
        
        
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'company_id', 'created_by']    


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'company', 'created_by', 'stages']            
        

class RoomMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomMember
        fields = ['id', 'user', 'room', 'role', 'status', 'created_at']
        
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'code', 'quantity', 'price', 'photo', 'qr_code', 'current_stage', 'room', 'created_by']                
        
 
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'room', 'user', 'type', 'status', 'created_at']        