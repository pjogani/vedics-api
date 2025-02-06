from rest_framework.permissions import IsAuthenticated
from core.viewsets import BaseModelViewSet
from django.db import models
from .models import UserProfile, ProfileQuestion, ProfileAnswer
from .serializers import (
    UserProfileSerializer,
    ProfileQuestionSerializer,
    ProfileAnswerSerializer
)
from .permissions import ProfilePermission


class UserProfileViewSet(BaseModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    # Now we enforce both standard authentication and our custom profile permission:
    permission_classes = [IsAuthenticated, ProfilePermission]

    def get_queryset(self):
        """
        - Superusers see all profiles.
        - Normal users see:
          1) Their own profile
          2) Any profile that has allow_org_access=True and belongs to
             at least one shared Organization.
        """
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()

        # Find the orgs the user belongs to:
        user_org_ids = user.team_memberships.values_list('team__organization_id', flat=True)

        return UserProfile.objects.filter(
            models.Q(user=user)
            | (
                models.Q(allow_org_access=True)
                & models.Q(user__team_memberships__team__organization_id__in=user_org_ids)
            )
        ).distinct()


class ProfileQuestionViewSet(BaseModelViewSet):
    queryset = ProfileQuestion.objects.all()
    serializer_class = ProfileQuestionSerializer
    permission_classes = [IsAuthenticated]


class ProfileAnswerViewSet(BaseModelViewSet):
    queryset = ProfileAnswer.objects.all()
    serializer_class = ProfileAnswerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        - Superusers see all answers.
        - Regular users see answers related to their own profile only.
        """
        user = self.request.user
        if user.is_superuser:
            return ProfileAnswer.objects.all()
        return ProfileAnswer.objects.filter(profile__user=user)
