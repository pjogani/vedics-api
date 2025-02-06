from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response

from core.mixins import BaseApiMixin
from .models import User
from .serializers import UserSerializer, CreateUserSerializer
from .permissions import IsUserOrSuperuserOrCreate


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    Provides CRUD for user accounts.
    Restricts listing all users to superusers only. Normal users
    can only view or update their own user record.

    create (POST): Anyone can sign up (no auth needed).
    list (GET): Only superusers can list all users.
    retrieve (GET), update (PUT/PATCH), destroy (DELETE):
        - Superusers can act on any user
        - A user can act on their own user object
    """
    queryset = User.objects.all()
    permission_classes = [IsUserOrSuperuserOrCreate]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer

    def get_queryset(self):
        """
        Superusers see all users;
        Regular users see only themselves.
        """
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
        return User.objects.filter(pk=user.pk)


class GoogleAuthTokenView(BaseApiMixin, APIView):
    """
    Example view showing how an authenticated user can retrieve their token.
    """
    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return self.unauthorised_response(
                message={"detail": "Authentication credentials were not provided."}
            )
        token, _ = Token.objects.get_or_create(user=request.user)
        return self.successful_response({"token": token.key})
