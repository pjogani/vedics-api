# File: /Users/pjo/Documents/repos/projects/vedics-api/assistant/views.py

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils.translation import gettext_lazy as _

from core.viewsets import BaseModelViewSet
from core.mixins import BaseApiMixin
from .conversation_manager import ConversationManager
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ChatView(BaseApiMixin, APIView):
    """
    Simple endpoint for sending a user message and getting the AI reply.
    POST data:
      - conversation_id (optional)
      - message (required)
    Returns:
      - reply (assistant's response)
      - conversation_id
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        conversation_id = request.data.get("conversation_id")
        user_input = request.data.get("message")

        if not user_input:
            return self.error_response(message=_("message is required"), status_code=400)

        manager = ConversationManager(request.user)
        result = manager.chat(conversation_id, user_input)
        return self.successful_response(
            message={
                "reply": result["reply"],
                "conversation_id": result["conversation_id"]
            },
            status_code=status.HTTP_200_OK
        )


class ConversationViewSet(BaseModelViewSet, viewsets.ModelViewSet):
    """
    Allows users to list or manage their own conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return conversations belonging to this user and not marked deleted.
        return Conversation.objects.filter(user=self.request.user, is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="close")
    def close_conversation(self, request, pk=None):
        """
        Mark a conversation as inactive.
        """
        conversation = self.get_object()
        conversation.is_active = False
        conversation.save()
        return self.successful_response(
            message={"message": _("Conversation closed.")},
            status_code=status.HTTP_200_OK
        )


class MessageViewSet(BaseModelViewSet, viewsets.ModelViewSet):
    """
    Allows users to view messages within their own conversations.
    Typically read-only (GET). Creating messages should go through ChatView.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            conversation__user=self.request.user,
            is_deleted=False
        )
