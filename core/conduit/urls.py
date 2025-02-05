from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ServiceViewSet, EndpointViewSet, APIRequestLogViewSet, ExternalCallViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'endpoints', EndpointViewSet, basename='endpoint')
router.register(r'logs', APIRequestLogViewSet, basename='logs')
router.register(r'external-call', ExternalCallViewSet, basename='external-call')

urlpatterns = [
    path('', include(router.urls)),
]