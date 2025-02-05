from django.db import models
from django.conf import settings
from core.mixins import AuthorTimeStampedModel

class UserProfile(AuthorTimeStampedModel):
    """
    Stores detailed Vedic-related information about a User.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    date_of_birth = models.DateField(null=True, blank=True)
    time_of_birth = models.TimeField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    # Optional: store the previously computed birth chart in JSON
    birth_chart = models.JSONField(default=dict, blank=True)
    preferred_language = models.CharField(max_length=10, default='en')


    def __str__(self):
        return f"Profile of {self.user.username}"


class ProfileQuestion(AuthorTimeStampedModel):
    """
    Represents a dynamic onboarding or profile question that can be shown to users.
    """
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=50, blank=True)  # e.g. text, number, select
    help_text = models.TextField(blank=True)

    def __str__(self):
        return self.question_text


class ProfileAnswer(AuthorTimeStampedModel):
    """
    Stores a user's answer to a given ProfileQuestion.
    """
    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        ProfileQuestion,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    answer_text = models.TextField(blank=True)

    def __str__(self):
        return f"Answer to '{self.question.question_text}' for {self.profile.user.username}"
