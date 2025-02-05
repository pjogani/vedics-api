# File: /Users/pjo/Documents/repos/projects/vedics-api/core/users/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from core.organizations.models import Organization
from .models import User
from profiles.models import UserProfile  # <-- NEW IMPORT for creating user profile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
        read_only_fields = ('id',)


class CreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer used for user registration and optional org creation/joining.
    """
    organization_id = serializers.UUIDField(
        required=False, allow_null=True, write_only=True,
        help_text="If provided, tries to join an existing organization."
    )
    organization_name = serializers.CharField(
        required=False, allow_blank=True, write_only=True,
        help_text="If provided (and no organization_id), creates a new org with this name. The user becomes an owner."
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'password', 'email', 'first_name', 'last_name',
            'auth_token', 'organization_id', 'organization_name'
        )
        read_only_fields = ('id', 'auth_token')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        org_id = attrs.get('organization_id')
        org_name = attrs.get('organization_name')

        if org_id and org_name:
            raise serializers.ValidationError(
                "Please provide either organization_id OR organization_name, not both."
            )
        return attrs

    def create(self, validated_data):
        org_id = validated_data.pop('organization_id', None)
        org_name = validated_data.pop('organization_name', '').strip()

        user = User.objects.create_user(**validated_data)
        # Create a token for the newly created user, if needed
        Token.objects.get_or_create(user=user)

        # If no org info is provided, create a brand-new organization automatically
        if not org_id and not org_name:
            new_org_name = f"{user.username}'s Organization"
            org = Organization.objects.create(name=new_org_name)
            org.add_user(user, role='owner')
        elif org_id:
            # If organization_id is given, try to join that org
            try:
                org = Organization.objects.get(id=org_id)
            except Organization.DoesNotExist:
                raise serializers.ValidationError(
                    f"Organization with id={org_id} does not exist."
                )
            try:
                org.add_user(user, role='member')
            except ValueError as e:
                raise serializers.ValidationError({"organization_id": str(e)})
        elif org_name:
            # If organization_name is given, create a new org, user is owner
            if Organization.objects.filter(name=org_name).exists():
                raise serializers.ValidationError(
                    f"Organization name '{org_name}' is already taken."
                )
            new_org = Organization.objects.create(name=org_name, subscription_plan='free', seats=5)
            new_org.add_user(user, role='owner')

        # Automatically create a UserProfile after the user is created
        UserProfile.objects.create(user=user)

        return user
