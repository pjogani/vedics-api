from django.db import models
from django.utils import timezone
from core.mixins import AuthorTimeStampedModel
from core.organizations.models import Organization

class SubscriptionPlan(AuthorTimeStampedModel):
    """
    Defines various subscription tiers. Example: 'free', 'premium', etc.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    monthly_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    max_seats = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Subscription(AuthorTimeStampedModel):
    """
    Associates an Organization with a SubscriptionPlan.
    A new Organization will be assigned the default 'free' plan if none is provided.
    """
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscriptions'
    )
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    @property
    def is_active(self):
        """
        If end_date is not set or is in the future, consider the subscription active.
        """
        if self.end_date is None:
            return True
        return self.end_date >= timezone.now().date()

    def __str__(self):
        return f"{self.organization.name} -> {self.plan.name if self.plan else 'No Plan'}"
