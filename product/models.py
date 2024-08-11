from django.contrib.auth.models import AbstractBaseUser, Group, Permission
from django.db import models

class User(AbstractBaseUser):
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company_id = models.CharField(max_length=100, unique=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'company_id']
    groups = models.ManyToManyField(
        Group,
        related_name='custom_product_user_set',  # Unique bir related_name kullanıyoruz.
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_product_user_permissions',  # Unique bir related_name kullanıyoruz.
        blank=True
    )

class Company(models.Model):
    name = models.CharField(max_length=255)
    company_id = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
    
class Room(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='rooms')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    stages = models.JSONField()  # Ürün aşamalarını saklamak için JSONField kullanıyoruz.
    
class RoomMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('editor', 'Editor'), ('member', 'Member')])
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('accepted', 'Accepted')])
    created_at = models.DateTimeField(auto_now_add=True)
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to='product_photos/')
    qr_code = models.CharField(max_length=255, unique=True)
    current_stage = models.CharField(max_length=100)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='products')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_products')
    
class Notification(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50, choices=[('invitation', 'Invitation'), ('product_added', 'Product Added'), ('product_updated', 'Product Updated')])
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
