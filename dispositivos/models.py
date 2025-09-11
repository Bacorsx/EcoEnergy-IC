from django.db import models
from django.core.validators import MinValueValidator
from core.models import BaseModel

class Organization(BaseModel):
    name  = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        db_table = "organization"
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return self.name


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
        return self.name


class Category(BaseModel):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="categories"
    )

    class Meta:
        db_table = "category"
        unique_together = (("organization", "name"),)
        ordering = ["name"]
        indexes = [
            models.Index(fields=["organization", "name"]),
            models.Index(fields=["organization"]),
        ]

    def __str__(self):
        return self.name


class Device(BaseModel):
    STATUS = (("ONLINE", "Online"), ("OFFLINE", "Offline"))
    status = models.CharField(max_length=10, choices=STATUS, default="ONLINE")
    name          = models.CharField(max_length=120)
    model         = models.CharField(max_length=120, blank=True, null=True)
    serial_number = models.CharField(max_length=120, blank=True, null=True)
    installed_at  = models.DateTimeField(blank=True, null=True)

    category      = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="devices"
    )
    zone          = models.ForeignKey(
        Zone, on_delete=models.PROTECT, related_name="devices"
    )
    organization  = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="devices"
    )

    class Meta:
        db_table = "device"
        unique_together = (("organization", "name"),)  # o ("organization","serial_number")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["organization"]),
            models.Index(fields=["category"]),
            models.Index(fields=["zone"]),
        ]

    def __str__(self):
        return self.name


class Measurement(BaseModel):
    value        = models.FloatField(validators=[MinValueValidator(0.0)])
    unit         = models.CharField(max_length=20)
    measured_at  = models.DateTimeField()

    device       = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="measurements"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="measurements"
    )

    class Meta:
        db_table = "measurement"
        ordering = ["-measured_at"]  # HU4: orden desc
        indexes = [
            models.Index(fields=["device"]),
            models.Index(fields=["organization"]),
            models.Index(fields=["-measured_at"]),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(value__gte=0), name="measurement_value_gte_0"),
        ]

    def __str__(self):
        return f"{self.device} @ {self.measured_at:%Y-%m-%d %H:%M}"


class Alert(BaseModel):
    SEVERITIES = (("GRAVE", "Grave"), ("ALTO", "Alto"), ("MEDIANO", "Mediano"))

    severity     = models.CharField(max_length=10, choices=SEVERITIES)
    message      = models.TextField()
    is_resolved  = models.BooleanField(default=False)
    resolved_at  = models.DateTimeField(blank=True, null=True)

    device       = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="alerts"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="alerts"
    )

    class Meta:
        db_table = "alert"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization"]),
            models.Index(fields=["device"]),
            models.Index(fields=["severity"]),
            models.Index(fields=["is_resolved"]),
        ]

    def __str__(self):
        return f"{self.get_severity_display()} - {self.device}"
