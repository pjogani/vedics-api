from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from .serializers import UserSerializer, CreateUserSerializer
from .models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    Provides CRUD for user accounts.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create','list']:
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer


class GoogleAuthTokenView(APIView):
    """
    Once the user has authenticated via Google (allauth) and has a valid session,
    they can hit this endpoint to retrieve/refresh their DRF token.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # If the user is authenticated via session,
        # generate or retrieve an existing auth token.
        token, _ = Token.objects.get_or_create(user=request.user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)
