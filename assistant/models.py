from django.db import models
from django.conf import settings
from core.mixins import AuthorTimeStampedModel


class ConversationMessage(AuthorTimeStampedModel):
    """
    Stores chat messages for the assistant feature.
    Includes user messages and assistant replies.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255)
    role = models.CharField(max_length=50)  # e.g. 'user', 'assistant', 'system'
    content = models.TextField()

    def __str__(self):
        return f"Session {self.session_id} - {self.role}"
