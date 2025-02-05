# File: /Users/pjo/Documents/repos/projects/vedics-api/core/organizations/views.py

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Organization, Team, TeamMembership
from .serializers import (
    OrganizationSerializer,
    TeamSerializer,
    TeamMembershipSerializer
)
from .permissions import IsOrganizationOwnerOrReadOnly, IsTeamAdminOrReadOnly
from core.mixins import BaseApiMixin

# NEW IMPORTS FOR LISTING PROFILES
from profiles.models import UserProfile
from profiles.serializers import UserProfileSerializer


class OrganizationViewSet(BaseApiMixin, viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsOrganizationOwnerOrReadOnly]

    def get_queryset(self):
        """
        Owners can see all orgs they own; superusers see all.
        Otherwise, only read orgs where user is part of at least one team or an owner.
        """
        user = self.request.user
        if user.is_superuser:
            return Organization.objects.all()
        return Organization.objects.filter(
            Q(owners=user) | Q(teams__memberships__user=user)
        ).distinct()

    @action(detail=True, methods=['get'], url_path='members')
    def members(self, request, pk=None):
        """
        Returns all user profiles belonging to this family (organization).
        """
        organization = self.get_object()
        user_ids = organization.teams.values_list('memberships__user', flat=True)
        user_profiles = UserProfile.objects.filter(user__in=user_ids).select_related('user')
        serializer = UserProfileSerializer(user_profiles, many=True)
        return Response(serializer.data)


class TeamViewSet(BaseApiMixin, viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated, IsTeamAdminOrReadOnly]

    def get_queryset(self):
        """
        Return teams that belong to organizations the user can access.
        Superusers see all.
        """
        user = self.request.user
        if user.is_superuser:
            return Team.objects.all()
        return Team.objects.filter(
            organization__owners=user
        ).union(
            Team.objects.filter(
                memberships__user=user
            )
        ).distinct()


class TeamMembershipViewSet(BaseApiMixin, viewsets.ModelViewSet):
    queryset = TeamMembership.objects.all()
    serializer_class = TeamMembershipSerializer
    permission_classes = [IsAuthenticated, IsTeamAdminOrReadOnly]

    def get_queryset(self):
        """
        Return memberships that the user can see:
          - If superuser, all.
          - Else if org owner or team admin, memberships for their org/teams.
          - Or the user's own membership.
        """
        user = self.request.user
        if user.is_superuser:
            return TeamMembership.objects.all()

        owned_orgs = Organization.objects.filter(owners=user)
        owned_teams = Team.objects.filter(organization__in=owned_orgs)
        admin_teams = Team.objects.filter(
            memberships__user=user,
            memberships__role='admin'
        )
        return TeamMembership.objects.filter(
            Q(team__in=owned_teams) |
            Q(team__in=admin_teams) |
            Q(user=user)
        ).distinct()
