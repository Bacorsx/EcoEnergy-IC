from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Measurement
from .services import generate_alert_events_for_measurement

@receiver(post_save, sender=Measurement)
def measurement_post_save(sender, instance: Measurement, created, **kwargs):
    # Para el test es suficiente con que se ejecute al crear
    if created:
        generate_alert_events_for_measurement(instance)
