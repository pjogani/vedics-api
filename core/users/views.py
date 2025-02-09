import uuid
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response

from core.mixins import BaseApiMixin
from profiles.models import UserProfile
from .models import User
from .serializers import UserSerializer, CreateUserSerializer
from .permissions import IsUserOrSuperuserOrCreate
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from google.oauth2 import id_token
import requests

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


class GoogleLoginView(SocialLoginView):
    def post(self, request, *args, **kwargs):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response(
                {'error': 'No access token provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch user info from Google using the access token
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        resp = requests.get(
            userinfo_url, 
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if resp.status_code != 200:
            return Response(
                {'error': 'Failed to fetch user info from Google'},
                status=status.HTTP_400_BAD_REQUEST
            )

        google_data = resp.json()
        # Typically includes keys like 'email', 'picture', 'name' etc.
        email = google_data.get('email')
        if not email:
            return Response(
                {'error': 'Email not provided by Google'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create user if doesn't exist
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            random_password = uuid.uuid4().hex[:8]
            serializer = CreateUserSerializer(data={
                'username': email.split('@')[0],
                'email': email,
                'password': random_password
            })
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

        # Return same response as UserViewSet create
        serializer = UserSerializer(user)
        data = serializer.data
        token, _ = Token.objects.get_or_create(user=user)
        data['token'] = token.key

        return Response(data)
