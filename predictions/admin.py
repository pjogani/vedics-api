from django.contrib import admin
from .models import UserReading

@admin.register(UserReading)
class UserReadingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reading_type', 'created_at')
    search_fields = ('user__username', 'reading_type')
