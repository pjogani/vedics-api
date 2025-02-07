from django.shortcuts import render
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from core.viewsets import BaseModelViewSet
from predictions.tasks import READING_TYPES
from .models import Prediction
from .serializers import DailyPredictionSerializer, LongTermPredictionSerializer


class DailyPredictionViewSet(BaseModelViewSet):
    serializer_class = DailyPredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Prediction.objects.filter(
            user=self.request.user,
            prediction_type="today_reading",
            is_deleted=False
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        # Get or create today's prediction
        prediction = self.get_queryset().first() or Prediction.objects.create(
            user=request.user,
            prediction_type="today_reading",
            content={}  # Will be generated in serializer
        )

        serializer = self.get_serializer(prediction)
        return self.successful_response(serializer.data)


class LongTermPredictionViewSet(BaseModelViewSet):
    serializer_class = LongTermPredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Prediction.objects.filter(
            user=self.request.user,
            prediction_type__in=READING_TYPES,
            is_deleted=False
        )

    def list(self, request, *args, **kwargs):
        # Get existing predictions
        queryset = self.get_queryset()
        # Generate any missing predictions
        user_profile = request.user.profile
        if user_profile.long_term_reading_status == "completed":
            self.get_serializer().create_missing_predictions(request.user)

        # Get updated queryset with new predictions
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.successful_response(serializer.data)

