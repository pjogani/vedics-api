from django.db import models
from django.conf import settings
from core.mixins import AuthorTimeStampedModel
from django.utils.translation import gettext_lazy as _  # <-- Added for translations

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
    title = models.CharField(_("Title"), max_length=255, blank=True, default="")
    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        # Translators: This is displayed in the admin or logs as an identifying string
        return _("Conversation %(id)s by %(username)s") % {
            "id": self.id,
            "username": self.user.username
        }


class Message(AuthorTimeStampedModel):
    """
    Individual chat message within a conversation.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    role = models.CharField(_("Role"), max_length=50)  # e.g. "user", "assistant", "system"
    content = models.TextField(_("Content"))

    def __str__(self):
        return _("Message %(id)s in Conversation %(conv_id)s - %(role)s") % {
            "id": self.id,
            "conv_id": self.conversation_id,
            "role": self.role
        }
