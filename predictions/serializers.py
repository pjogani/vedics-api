from rest_framework import serializers
from django.utils import timezone

from predictions.tasks import generate_missing_predictions_for_user
from .models import Prediction
from .services.reading_service import ReadingService

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ['id', 'prediction_type', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Ensure user is set from context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DailyPredictionSerializer(PredictionSerializer):
    def to_representation(self, instance):
        # Get today's date in the user's timezone
        today = timezone.now().date()

        # If the prediction is from today, return it
        if instance.created_at.date() == today and instance.content:
            return super().to_representation(instance)
        # Otherwise, generate a new prediction
        reading_service = ReadingService()
        prediction = reading_service.generate_reading(
            user=instance.user,
            reading_type="today_reading"
        )
        return super().to_representation(prediction)


class LongTermPredictionSerializer(PredictionSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def create(self, validated_data):
        reading_service = ReadingService()
        user = self.context['request'].user

        # Generate content for the specific reading type
        prediction = reading_service.generate_reading(
            user=user,
            reading_type=validated_data['prediction_type']
        )
        validated_data['content'] = prediction.content
        validated_data['user'] = user
        return super().create(validated_data)

    def create_missing_predictions(self, user):
        """
        Helper method to create any missing prediction types for a user
        """
        generate_missing_predictions_for_user.delay(user.id)
