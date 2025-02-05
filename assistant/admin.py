from django.contrib import admin
from .models import ConversationMessage

@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'role', 'created_at')
    search_fields = ('user__username', 'session_id', 'role')
