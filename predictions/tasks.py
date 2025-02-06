from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Prediction
from .services.reading_service import ReadingService

User = get_user_model()

READING_TYPES = [
    "core_personality_and_life_path",
    "career_success_and_wealth",
    "relationships_love_and_marriage",
    "health_and_wellbeing",
    "challenges_and_remedies",
    "major_life_periods"
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
    if not missing_types:
        return

    user_profile.long_term_reading_status = "pending"
    user_profile.save()

    for reading_type in missing_types:
        prediction = reading_service.generate_reading(
            user=user,
            reading_type=reading_type
        )
        new_predictions.append(
            Prediction.objects.create(
                user=user,
                prediction_type=reading_type,
                content=prediction.content
            )
        )

    user_profile.long_term_reading_status = "completed"
    user_profile.save()

    return new_predictions



@shared_task(name="generate_all_readings_for_user")
def generate_all_readings_for_user(user_id):
    """
    A Celery task that generates multiple reading types for a given user.
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return f"User {user_id} does not exist."

    user_profile = user.profile
    user_profile.long_term_reading_status = "pending"
    user_profile.save()
    reading_service = ReadingService()
    reading_types = [
        "core_personality_and_life_path",
        "career_success_and_wealth",
        "relationships_love_and_marriage",
        "health_and_wellbeing",
        "challenges_and_remedies",
        "major_life_periods",
    ]
    results = {}

    Prediction.objects.filter(
        user_id=user_id,
        prediction_type__in=reading_types
    ).update(is_deleted=True)

    for rtype in reading_types:
        prediction = reading_service.generate_reading(user, reading_type=rtype)
        results[rtype] = prediction.content

    user_profile.long_term_reading_status = "completed"
    user_profile.save()
    return results


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
