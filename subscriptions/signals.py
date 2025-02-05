from django.db.models.signals import post_save
from django.dispatch import receiver
from core.organizations.models import Organization
from .models import Subscription, SubscriptionPlan

@receiver(post_save, sender=Organization)
def assign_free_subscription(sender, instance, created, **kwargs):
    """
    Whenever a new Organization is created, automatically assign it a 'free' subscription
    if it doesn't already have one.
    """
    if created:
        # Ensure we have a 'free' plan in the DB, or create it
        free_plan, _ = SubscriptionPlan.objects.get_or_create(
            name='free',
            defaults={
                'description': 'Default free tier',
                'monthly_price': 0.00,
                'max_seats': 5,
                'is_active': True,
            }
        )
        # Create the Subscription if none exists
        Subscription.objects.get_or_create(
            organization=instance,
            defaults={'plan': free_plan}
        )
