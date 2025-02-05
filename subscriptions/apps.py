from django.apps import AppConfig

class SubscriptionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "subscriptions"

    def ready(self):
        # This will import signals so that the post_save handlers are registered.
        import subscriptions.signals  # noqa
