from django.db import models
from django.conf import settings
from core.mixins import AuthorTimeStampedModel

class Prediction(AuthorTimeStampedModel):
    """
    Stores a user's generated reading (daily, career, relationship, etc.).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prediction_type = models.CharField(max_length=100)  # e.g. "daily", "career", etc.
    content = models.JSONField()

    def __str__(self):
        return f"{self.user.username} - {self.prediction_type}"
