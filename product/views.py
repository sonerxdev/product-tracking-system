from django.shortcuts import render
from rest_framework import viewsets
from .models import User, Company, Room, RoomMember, Product, Notification
from .serializers import UserSerializer, CompanySerializer, RoomSerializer, RoomMemberSerializer, ProductSerializer, NotificationSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]   
    

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    

class RoomMemberViewSet(viewsets.ModelViewSet):
    queryset = RoomMember.objects.all()
    serializer_class = RoomMemberSerializer
    permission_classes = [IsAuthenticated]
    
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]               
    
    
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]    