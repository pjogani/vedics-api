from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Prediction
from .services.reading_service import ReadingService

User = get_user_model()


@shared_task(name="generate_all_readings_for_user")
def generate_all_readings_for_user(user_id):
    """
    A Celery task that generates multiple reading types for a given user.
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return f"User {user_id} does not exist."

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

    for rtype in reading_types:
        content = reading_service.generate_reading(user, reading_type=rtype)
        results[rtype] = content

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
