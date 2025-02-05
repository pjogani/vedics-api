from django.db import models
from django.conf import settings
from core.mixins import AuthorTimeStampedModel

class UserReading(AuthorTimeStampedModel):
    """
    Stores a user's generated reading (daily, career, relationship, etc.).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reading_type = models.CharField(max_length=100)
    content = models.JSONField()

    def __str__(self):
        return f"{self.user.username} - {self.reading_type}"
