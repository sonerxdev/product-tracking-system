import random
import uuid
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import Room, Notification, Product, RoomMember, User, Company
from .serializers import UserSerializer, RoomSerializer, ProductSerializer, NotificationSerializer, RoomMemberSerializer, CompanySerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
import rest_framework

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

## phone number hariç diğer bilgiler zorunlu değil
## diğer bilgier null olarak gönderilebilir

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    phone_number = request.data.get('phone_number')
    
    if not phone_number:
        return Response({'error': 'Telefon numarası zorunludur.'}, status=status.HTTP_400_BAD_REQUEST)
    
    user, created = User.objects.get_or_create(phone_number=phone_number)
    
    # Diğer bilgileri güncelle (eğer varsa)
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    company_id = request.data.get('company_id')
    
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    if company_id is not None:
        user.company_id = company_id
    
    user.save()
    
    try:
        tokens = get_tokens_for_user(user)
    except Exception as e:
        return Response({'error': f'Token oluşturulurken hata oluştu: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if created:
        return Response({'message': 'Kullanıcı başarıyla kaydedildi.', **tokens}, status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'Kullanıcı zaten kayıtlı.', **tokens}, status=status.HTTP_200_OK)

## request body for register_user
# { "phone_number": "5551234567", "first_name": "John", "last_name": "Doe", "company_id": "123456" }
## response body for register_user
# { "message": "Kullanıcı başarıyla kaydedildi.", "refresh ": "eyJ0eXA ...", "access ": "eyJ0eXA ..." } 


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_info(request):
    user = request.user
    
    # Güncellenebilir alanlar
    fields = ['first_name', 'last_name']
    
    for field in fields:
        value = request.data.get(field)
        if value is not None:
            setattr(user, field, value)
    
    # company_id'yi ayrıca ele al
    company_id = request.data.get('company_id')
    if company_id is not None:
        # Eğer bu company_id'ye sahip bir şirket varsa, kullanıcıyı bu şirkete bağla
        if Company.objects.filter(company_id=company_id).exists():
            user.company_id = company_id
        else:
            return Response({'error': 'Geçersiz company_id'}, status=status.HTTP_400_BAD_REQUEST)
    
    user.save()
    
    # Güncellenmiş kullanıcı bilgilerini döndür
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

## request body for update_user_info
# { "first_name": "John", "last_name": "Doe", "company_id": "123456" }
## response body for update_user_info
# { "first_name": "John", "last_name": "Doe", "company_id": "123456" }



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
@permission_classes([IsAuthenticated])
def create_room(request):
    name = request.data.get('name')
    stages = request.data.get('stages')
    
    if not name or not stages:
        return Response({'error': 'Oda adı ve aşamalar zorunludur.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Şirket ID'sini oluştur
    company_id = f"COMP-{uuid.uuid4().hex[:8].upper()}"
    
    # Şirketi oluştur
    company = Company.objects.create(
        name=name,  # Oda adını şirket adı olarak kullan
        company_id=company_id,
        created_by=request.user
    )
    
    # Odayı oluştur
    room = Room.objects.create(
        name=name,
        company=company,
        created_by=request.user,
        stages=stages
    )
    
    # Odayı oluşturan kişiyi admin olarak ekle
    RoomMember.objects.create(
        user=request.user,
        room=room,
        role='admin',
        status='accepted'
    )
    
    # Kullanıcının company_id'sini güncelle
    request.user.company_id = company_id
    request.user.save()
    
    serializer = RoomSerializer(room)
    return Response({
        'room': serializer.data,
        'company_id': company_id
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_details(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
        room_members = RoomMember.objects.filter(room=room)
        product_count = Product.objects.filter(room=room).count()
        
        room_serializer = RoomSerializer(room)
        company_serializer = CompanySerializer(room.company)
        member_serializer = RoomMemberSerializer(room_members, many=True)
        
        response_data = {
            'room': room_serializer.data,
            'company': company_serializer.data,
            'members': member_serializer.data,
            'product_count': product_count
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    except Room.DoesNotExist:
        return Response({'error': 'Oda bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def home_page(request):
    user = request.user
    print(f"User ID: {user.id}")
    print(f"User Phone: {user.phone_number}")
    
    if not user.is_authenticated:
        return Response({
            'detail': 'Kullanıcı kimliği doğrulanamadı.',
            'code': 'authentication_failed'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Kullanıcının ait olduğu odayı bul
        room_member = RoomMember.objects.filter(user=user).first()
        
        if room_member:
            room = room_member.room
            products = Product.objects.filter(room=room)
            product_serializer = ProductSerializer(products, many=True)
            room_serializer = RoomSerializer(room)
            
            return Response({
                'has_room': True,
                'room': room_serializer.data,
                'products': product_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'has_room': False,
                'message': 'Henüz bir odaya katılmadınız veya oda oluşturmadınız.'
            }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'detail': f'Bir hata oluştu: {str(e)}',
            'code': 'server_error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

## renew access token
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    serializer = TokenRefreshView().get_serializer(data=request.data)
    
    try:
        serializer.is_valid(raise_exception=True)
    except TokenError as e:
        raise InvalidToken(e.args[0])
    
    return Response(serializer.validated_data, status=status.HTTP_200_OK)

