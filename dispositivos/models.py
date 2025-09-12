# dispositivos/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Q  
from core.models import BaseModel, Organization



class Zone(BaseModel):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="zones"
    )

    class Meta:
        db_table = "zone"
        unique_together = (("organization", "name"),)
        ordering = ["name"]
        indexes = [
            models.Index(fields=["organization", "name"]),
            models.Index(fields=["organization"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Category(BaseModel):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "category"
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return self.name


class Device(BaseModel):
    name = models.CharField(max_length=150)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    installed_at = models.DateTimeField(blank=True, null=True)

    zone = models.ForeignKey(
        Zone, on_delete=models.PROTECT, related_name="devices"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="devices"
    )

    class Meta:
        db_table = "device"
        unique_together = (("organization", "serial_number"),)
        ordering = ["name"]
        indexes = [
            models.Index(fields=["organization"]),
            models.Index(fields=["zone"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Product(BaseModel):
    name = models.CharField(max_length=150)
    model = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)

    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="products",
        null=True, blank=True
    )

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )

    class Meta:
        db_table = "product"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["device"]),
            models.Index(fields=["category"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["device", "serial_number"],
                name="uq_products_device_serial_nonnull",
                condition=Q(device__isnull=False)
            ),
            models.UniqueConstraint(
                fields=["serial_number"],
                name="uq_products_serial_when_device_null",
                condition=Q(device__isnull=True),
            )
        ]

    def __str__(self):
        return self.name if not self.device else f"{self.name} ({self.device.name})"


class Measurement(BaseModel):
    value = models.FloatField(validators=[MinValueValidator(0.0)])
    unit = models.CharField(max_length=20)
    measured_at = models.DateTimeField()
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="measurements")

    class Meta:
        db_table = "measurement"
        ordering = ["-measured_at"]
        indexes = [models.Index(fields=["product"]), models.Index(fields=["-measured_at"])]
    def __str__(self):
        return f"{self.product.name} — {self.value} {self.unit} @ {self.measured_at:%Y-%m-%d %H:%M}"
    
class Alert(BaseModel):
    SEVERITIES = (("GRAVE","Grave"),("ALTO","Alto"),("MEDIANO","Mediano"))
    severity   = models.CharField(max_length=10, choices=SEVERITIES)
    message    = models.TextField(blank=True, default="")
    class Meta:
        db_table = "alert"
    def __str__(self):
        return self.get_severity_display()


# Quiebre Product ↔ Alert con rangos
class ProductAlert(BaseModel):
    product   = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='alert_links')
    alert     = models.ForeignKey('Alert',   on_delete=models.CASCADE, related_name='product_links')
    range_min = models.FloatField()
    range_max = models.FloatField()
    unit      = models.CharField(max_length=16)
    class Meta:
        db_table = "product_alert"
        unique_together = (("product","alert"),)
    def __str__(self):
        sev = self.alert.get_severity_display()
        return f"{self.product.name} · {sev} [{self.range_min}–{self.range_max} {self.unit}]"
    
# Evento de alerta disparado por una medición
class ProductAlertEvent(BaseModel):
    product_alert = models.ForeignKey('ProductAlert', on_delete=models.CASCADE, related_name='events')
    measurement   = models.ForeignKey('Measurement',  on_delete=models.CASCADE, related_name='alert_events')
    is_resolved   = models.BooleanField(default=False)
    resolved_at   = models.DateTimeField(blank=True, null=True)
    class Meta:
        db_table = "product_alert_event"
    
    def __str__(self):
        sev = self.product_alert.alert.get_severity_display()
        p = self.product_alert.product.name
        v = f"{self.measurement.value} {self.measurement.unit}"
        return f"{p} · {sev} · {v} @ {self.measurement.measured_at:%Y-%m-%d %H:%M}"