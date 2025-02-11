from datetime import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from core.conduit.utils import get_coordinates
from predictions.models import Prediction
from .models import UserProfile
from predictions.services.astro_service import AstroService
from predictions.tasks import READING_TYPES, generate_missing_predictions_for_user, generate_missing_predictions_for_user

@receiver(pre_save, sender=UserProfile)
def update_coordinates(sender, instance, **kwargs):
    """
    Update coordinates and birth chart when place_of_birth, date_of_birth, or time_of_birth is changed
    """
    if not instance.pk:  # New instance
        if instance.place_of_birth:
            coordinates = get_coordinates(instance.place_of_birth)
            birth_chart = AstroService().calculate_birth_chart(
                date_of_birth=instance.date_of_birth,
                time_of_birth=instance.time_of_birth,
                lat=coordinates['latitude'],
                lon=coordinates['longitude']
            )

            instance.latitude = coordinates['latitude']
            instance.longitude = coordinates['longitude']
            instance.birth_chart = birth_chart
            instance._generate_readings = True
        return

    old_instance = UserProfile.objects.get(pk=instance.pk)
    fields_changed = any([
        instance.place_of_birth != old_instance.place_of_birth,
        instance.date_of_birth != old_instance.date_of_birth,
        instance.time_of_birth != old_instance.time_of_birth,
        instance.preferred_language != old_instance.preferred_language
    ])

    if fields_changed and instance.place_of_birth:
        coordinates = get_coordinates(instance.place_of_birth)
        birth_chart = AstroService().calculate_birth_chart(
            date_of_birth=instance.date_of_birth,
            time_of_birth=instance.time_of_birth,
            lat=coordinates['latitude'],
            lon=coordinates['longitude']
        )

        instance.latitude = coordinates['latitude']
        instance.longitude = coordinates['longitude']
        instance.birth_chart = birth_chart
        instance.long_term_reading_status = 'reeval'
        # Schedule task to generate readings after save
        instance._generate_readings = True  # Flag to use in post_save


@receiver(post_save, sender=UserProfile)
def generate_readings(sender, instance, created, **kwargs):
    """
    Generate readings when birth chart is updated
    """
    if hasattr(instance, '_generate_readings'):
        reading_types = READING_TYPES + ["todays_reading"]
        Prediction.objects.filter(
            user_id=instance.user.id,
            prediction_type__in=reading_types
        ).update(is_deleted=True)
        generate_missing_predictions_for_user.delay(instance.user.id)
