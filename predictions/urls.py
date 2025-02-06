from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DailyPredictionViewSet, LongTermPredictionViewSet

router = DefaultRouter()
router.register(r'daily', DailyPredictionViewSet, basename='daily-prediction')
router.register(r'longterm', LongTermPredictionViewSet, basename='longterm-prediction')

urlpatterns = [
    path('', include(router.urls)),
]
