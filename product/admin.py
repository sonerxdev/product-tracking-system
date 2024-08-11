
# Register your models here.

from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'first_name', 'last_name')
    search_fields = ('phone_number', 'first_name', 'last_name')
