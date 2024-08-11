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

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    phone_number = request.data.get('phone_number')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    company_id = request.data.get('company_id')

    if User.objects.filter(phone_number=phone_number).exists():
        return Response({'detail': 'Bu telefon numarası ile kayıtlı bir kullanıcı zaten var.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User(phone_number=phone_number, first_name=first_name, last_name=last_name, company_id=company_id)
    user.save()
    tokens = get_tokens_for_user(user)
    return Response(tokens, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    phone_number = request.data.get('phone_number')
    try:
        user = User.objects.get(phone_number=phone_number)
        tokens = get_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'detail': 'Kullanıcı bulunamadı'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
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