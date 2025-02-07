from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Prediction
from .services.reading_service import ReadingService

User = get_user_model()

READING_TYPES = [
    "career_finance",
    "relationships_love",
    "health_wellness",
    "spiritual_growth",
    "strengths_weaknesses",
    "challenges_remedies",
    "family_social",
    "travel_settlements",
    "wealth_luck",
]

@shared_task(name="generate_missing_predictions_for_user")
def generate_missing_predictions_for_user(user_id):
    """
    Generate missing predictions for a user.
    """
    user = User.objects.get(pk=user_id)
    user_profile = user.profile
    reading_service = ReadingService()
    existing_types = set(
        Prediction.objects.filter(
            user=user,
            prediction_type__in=READING_TYPES,
            is_deleted=False
        ).values_list('prediction_type', flat=True)
    )

    missing_types = set(READING_TYPES) - existing_types
    new_predictions = []
    if (not missing_types or user_profile.long_term_reading_status == "pending"):
        return

    user_profile.long_term_reading_status = "pending"
    user_profile.save()

    for reading_type in missing_types:
        reading_service.generate_reading(
            user=user,
            reading_type=reading_type
        )

    user_profile.long_term_reading_status = "completed"
    user_profile.save()

    return {"message": "Predictions generated successfully"}



@shared_task(name="generate_daily_reading_for_all_users")
def generate_daily_reading_for_all_users():
    """
    Optionally, you could run a daily job generating a "today" reading
    for all active users.
    """
    reading_service = ReadingService()
    users = User.objects.all()
    count = 0

    for user in users:
        reading_service.generate_reading(user, reading_type="today_reading")
        count += 1

    return f"Generated daily reading for {count} users."
