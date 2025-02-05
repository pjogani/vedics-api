from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatView, ConversationViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='assistant-conversations')
router.register(r'messages', MessageViewSet, basename='assistant-messages')

urlpatterns = [
    # Chat endpoint: simple user->assistant conversation
    path('chat/', ChatView.as_view(), name='assistant-chat'),
    # CRUD endpoints for conversations and messages
    path('', include(router.urls)),
]
