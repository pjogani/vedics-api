from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import OrganizationViewSet, TeamViewSet, TeamMembershipViewSet

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')  # Typically not needed here
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'memberships', TeamMembershipViewSet, basename='membership')

urlpatterns = [
    path('', include(router.urls)),
]
