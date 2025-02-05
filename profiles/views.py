from rest_framework.permissions import IsAuthenticated
from core.viewsets import BaseModelViewSet
from .models import UserProfile, ProfileQuestion, ProfileAnswer
from .serializers import (
    UserProfileSerializer,
    ProfileQuestionSerializer,
    ProfileAnswerSerializer
)

class UserProfileViewSet(BaseModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        - Superusers can view all profiles.
        - Regular users can only view their own profile.
        """
        user = self.request.user
        if user.is_superuser:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=user)


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
