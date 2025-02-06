from django.db import models
from django.conf import settings
from core.mixins import AuthorTimeStampedModel

class Conversation(AuthorTimeStampedModel):
    """
    Represents a conversation session for the assistant.
    Linked to the user who initiated it.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations"
    )
    title = models.CharField(max_length=255, blank=True, default="")
    is_active = models.BooleanField(default=True)
    session_id = models.CharField(max_length=100, blank=False, null=True)
    thread_id = models.CharField(max_length=100, blank=False, null=True)
    assistant_id = models.CharField(max_length=100, blank=False, null=True)

    def __str__(self):
        return f"Conversation {self.id} by {self.user.username}"


class Message(AuthorTimeStampedModel):
    """
    Individual chat message within a conversation.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    role = models.CharField(max_length=50)  # e.g. "user", "assistant", "system"
    content = models.TextField()

    def __str__(self):
        return f"Message {self.id} in Conversation {self.conversation_id} - {self.role}"
