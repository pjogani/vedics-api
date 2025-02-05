from rest_framework import serializers
from .models import Conversation, Message

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            'id', 'user', 'title', 'is_active',
            'created_at', 'updated_at', 'is_deleted'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'is_deleted']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'role', 'content',
            'created_at', 'updated_at', 'is_deleted'
        ]
        read_only_fields = ['id', 'conversation', 'created_at', 'updated_at', 'is_deleted']
