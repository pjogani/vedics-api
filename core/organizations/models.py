from django.conf import settings
from django.db import models
from core.mixins import AuthorTimeStampedModel

class Organization(AuthorTimeStampedModel):
    """
    Represents a paying or otherwise subscribed organization.
    Seats define how many distinct users can be part of this Org.
    Owners can manage subscription details, add seats, etc.
    """
    name = models.CharField(max_length=255, unique=True)
    subscription_plan = models.CharField(max_length=100, default='free', blank=True)
    seats = models.PositiveIntegerField(default=5)
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='owned_organizations'
    )

    def __str__(self):
        return self.name

    def current_seat_usage(self):
        """
        Returns the count of distinct users across all teams in this organization.
        """
        team_ids = self.teams.values_list('id', flat=True)
        distinct_user_count = TeamMembership.objects.filter(team_id__in=team_ids).values('user').distinct().count()
        return distinct_user_count

    def has_available_seat_for(self, user):
        """
        Checks whether this organization can add `user` without exceeding seats.
        If the user is already in any team of the org, no extra seat is needed.
        Otherwise, we must confirm seat availability.
        """
        # If user is already in the organization, no new seat is used
        team_ids = self.teams.values_list('id', flat=True)
        user_exists = TeamMembership.objects.filter(team_id__in=team_ids, user=user).exists()
        if user_exists:
            return True

        # If not present, check if there's an available seat
        if self.current_seat_usage() < self.seats:
            return True
        return False

    def add_user(self, user, role='member'):
        """
        Utility method to add a user to the organization. Checks seat availability,
        creates (or reuses) a default team, optionally sets the user as an owner.
        Raise ValueError if seats are unavailable.
        """
        if not self.has_available_seat_for(user):
            raise ValueError(f"No available seats in the organization '{self.name}'.")

        # Optionally place the user in a default or "General" team
        default_team, _ = self.teams.get_or_create(name="General", defaults={
            "organization": self,
        })

        # If the user is not in the team, create membership
        membership, created = TeamMembership.objects.get_or_create(
            team=default_team,
            user=user,
            defaults={"role": role},
        )

        # If role is 'admin' or 'owner' and you also want them in owners:
        if role == 'owner':
            self.owners.add(user)

        return membership


class Team(AuthorTimeStampedModel):
    """
    A team belongs to one organization. A user can be in multiple teams.
    """
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='teams'
    )

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class TeamMembership(AuthorTimeStampedModel):
    """
    Many-to-many link between users and teams with a role designation.
    For example: "admin", "member", "owner".
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('owner', 'Owner'),  # optional: can treat the 'owner' role specially
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member'
    )

    def __str__(self):
        return f"{self.user.username} in {self.team.name} as {self.role}"


# Avoid circular import issues
# If needed, import TeamMembership after it's declared
from .models import TeamMembership  # type: ignore
