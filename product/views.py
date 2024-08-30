import random
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import Room, Notification, Product, RoomMember, User
from .serializers import UserSerializer, RoomSerializer, ProductSerializer, NotificationSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

## phone number hariç diğer bilgiler zorunlu değil
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    phone_number = request.data.get('phone_number')
    user, created = User.objects.get_or_create(phone_number=phone_number)
    tokens = get_tokens_for_user(user)
    if created:
        return Response({'message': 'Kullanıcı başarıyla kaydedildi.', **tokens}, status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'Kullanıcı zaten kayıtlı.', **tokens}, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_info(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

## request body for register_user
# { "phone_number": "5551234567", "first_name": "John", "last_name": "Doe", "company_id": "123456" }
## response body for register_user
# { "refresh ": "eyJ0eXA ...", "access ": "eyJ0eXA ..." } 


@api_view(['GET'])
@permission_classes([AllowAny])
def is_registered(request):
    phone_number = request.query_params.get('phone_number')
    if User.objects.filter(phone_number=phone_number).exists():
        return Response({'is_registered': True}, status=status.HTTP_200_OK)
    return Response({'is_registered': False}, status=status.HTTP_200_OK)

## example usage of is_registered
# GET /is_registered/?phone_number=5551234567
 

@api_view(['POST'])
@permission_classes([AllowAny])
def create_room(request):
    serializer = RoomSerializer(data=request.data)
    if serializer.is_valid():
        room = serializer.save(created_by=request.user)
        RoomMember.objects.create(user=request.user, room=room, role='admin', status='accepted')
        return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_rooms(request):
    rooms = Room.objects.filter(members__user=request.user)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def room_detail(request, room_id):
    try:
        room = Room.objects.get(id=room_id, members__user=request.user)
        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
    except Room.DoesNotExist:
        return Response({'detail': 'Oda bulunamadı veya erişim izniniz yok.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def add_product(request, room_id):
    try:
        room = Room.objects.get(id=room_id, members__user=request.user)
    except Room.DoesNotExist:
        return Response({'detail': 'Oda bulunamadı veya erişim izniniz yok.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save(created_by=request.user, room=room)
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id, room__members__user=request.user)
        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'detail': 'Ürün bulunamadı veya erişim izniniz yok.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def list_notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)