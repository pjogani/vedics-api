from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles"


    def ready(self):
        print("Registering profiles signals...")
        import profiles.signals  # noqa
        print("Profiles signals registered successfully")
