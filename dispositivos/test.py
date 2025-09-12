# Create your tests here.
from django.test import TestCase
from django.utils import timezone
from core.models import Organization
from dispositivos.models import Zone, Category, Device, Product, Alert, ProductAlert, ProductAlertEvent, Measurement

class AlertPipelineTest(TestCase):
    def setUp(self):
        org = Organization.objects.create(name="Org Test")
        zone = Zone.objects.create(name="Zona Test", organization=org)
        cat  = Category.objects.create(name="Cat Test")
        dev  = Device.objects.create(name="Dev Test", organization=org, zone=zone)
        self.prod = Product.objects.create(name="Prod Test", category=cat, device=dev)

        a_g, _ = Alert.objects.get_or_create(severity="GRAVE",   defaults={"message": "Alerta Grave"})
        a_h, _ = Alert.objects.get_or_create(severity="ALTO",    defaults={"message": "Alerta Alto"})
        a_m, _ = Alert.objects.get_or_create(severity="MEDIANO", defaults={"message": "Alerta Mediano"})

        ProductAlert.objects.create(product=self.prod, alert=a_m, range_min=70, range_max=80, unit="°C")
        ProductAlert.objects.create(product=self.prod, alert=a_h, range_min=81, range_max=90, unit="°C")
        ProductAlert.objects.create(product=self.prod, alert=a_g, range_min=91, range_max=9_999_999, unit="°C")

    def test_event_created_for_high(self):
        m = Measurement.objects.create(product=self.prod, value=85, unit="°C", measured_at=timezone.now())
        evts = ProductAlertEvent.objects.filter(measurement=m)
        self.assertEqual(evts.count(), 1)
        self.assertEqual(evts.first().product_alert.alert.severity, "ALTO")
