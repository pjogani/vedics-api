from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import SubscriptionPlanViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register(r'plans', SubscriptionPlanViewSet, basename='subscription-plan')
router.register(r'', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    # e.g. /api/v1/subscriptions/plans/ and /api/v1/subscriptions/
    path('', include(router.urls)),
]
