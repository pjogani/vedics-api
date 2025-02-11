# File: /Users/pjo/Documents/repos/projects/vedics-api/profiles/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model

from core.conduit.utils import get_coordinates
from .models import UserProfile, ProfileQuestion, ProfileAnswer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Minimal nested serializer to display the User associated with a Profile.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Handles creation/update of a user profile. Includes read-only user details.
    """
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True, required=False)

    def validate_place_of_birth(self, value):
        """
        Validate place_of_birth by checking if valid coordinates can be obtained.
        """
        if value:
            coordinates = get_coordinates(value)
            lat = coordinates['latitude']
            lon = coordinates['longitude']
            if lat == 0 and lon == 0:
                raise serializers.ValidationError("Invalid Place of birth")
        return value


    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'user_id',
            'date_of_birth',
            'time_of_birth',
            'place_of_birth',
            'phone_number',
            'preferred_language',
            'area_of_interests',
            'long_term_reading_status',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'is_deleted',
            'created_at',
            'updated_at',
        ]

    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None)
        user = None
        if user_id:
            user = User.objects.get(pk=user_id)
        profile = UserProfile.objects.create(user=user, **validated_data)
        return profile


class ProfileQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileQuestion
        fields = [
            'id',
            'question_text',
            'question_type',
            'help_text',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'is_deleted',
            'created_at',
            'updated_at',
        ]


class ProfileAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileAnswer
        fields = [
            'id',
            'profile',
            'question',
            'answer_text',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
