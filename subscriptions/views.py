from rest_framework.permissions import IsAuthenticated
from core.viewsets import BaseModelViewSet
from .models import SubscriptionPlan, Subscription
from .serializers import SubscriptionPlanSerializer, SubscriptionSerializer

class SubscriptionPlanViewSet(BaseModelViewSet):
    """
    Viewset for CRUD operations on SubscriptionPlans.
    Typically only staff might create or update plans.
    """
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SubscriptionPlan.objects.filter(is_deleted=False, is_active=True)


class SubscriptionViewSet(BaseModelViewSet):
    """
    Manages the association between an Organization and a SubscriptionPlan.
    If you want only org owners to update their subscription, add custom checks here.
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Subscription.objects.filter(is_deleted=False)

        # Return only the subscription(s) for organizations the user can manage or view
        # For example: organizations that user owns or is a member of
        return Subscription.objects.filter(
            organization__teams__memberships__user=user,
            is_deleted=False
        ).distinct()
