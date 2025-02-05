from rest_framework import serializers
from django.db import transaction
from .models import Organization, Team, TeamMembership
from django.contrib.auth import get_user_model

User = get_user_model()

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'subscription_plan', 'seats', 'owners',
            'created_at', 'updated_at', 'is_deleted'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['current_seat_usage'] = instance.current_seat_usage()
        return data


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'organization',
            'created_at', 'updated_at', 'is_deleted'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class TeamMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMembership
        fields = [
            'id', 'team', 'user', 'role',
            'created_at', 'updated_at', 'is_deleted'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate(self, attrs):
        """
        Check seat constraints if user is not already in the organization.
        """
        team = attrs.get('team')
        user = attrs.get('user')
        if team and user:
            org = team.organization
            if not org.has_available_seat_for(user):
                raise serializers.ValidationError(
                    f"No available seats in the organization '{org.name}'."
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        return super().create(validated_data)


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
