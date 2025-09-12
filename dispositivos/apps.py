from django.apps import AppConfig

class DispositivosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dispositivos"

    def ready(self):
        # registra señales
        from . import signals  # noqa