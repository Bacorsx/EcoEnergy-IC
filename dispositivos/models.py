from django.db import models
from usuarios.models import Organization, BaseModel


class Category(BaseModel):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "categories"
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="uq_categories_org_name"),
        ]

    def __str__(self):
        return self.name


class Zone(BaseModel):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="zones"
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "zones"
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="uq_zones_org_name"),
        ]

    def __str__(self):
        return self.name


class DeviceStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    MAINTENANCE = "maintenance", "Maintenance"


class Device(BaseModel):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="devices"
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="devices")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="devices")
    name = models.CharField(max_length=120)
    model = models.CharField(max_length=120, null=True, blank=True)
    serial_number = models.CharField(max_length=120, null=True, blank=True)
    status = models.CharField(
        max_length=12, choices=DeviceStatus.choices, default=DeviceStatus.ACTIVE
    )
    installed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "devices"
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="uq_devices_org_name"),
            models.UniqueConstraint(fields=["organization", "serial_number"], name="uq_devices_org_serial"),
        ]

    def __str__(self):
        return self.name


class Measurement(BaseModel):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="measurements"
    )
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="measurements")
    measured_at = models.DateTimeField()
    value = models.FloatField()
    unit = models.CharField(max_length=30, default="kWh")

    class Meta:
        db_table = "measurements"
        ordering = ["-measured_at"]

    def __str__(self):
        return f"{self.device.name} - {self.value}{self.unit}"


class AlertSeverity(models.TextChoices):
    CRITICAL = "critical", "Critical"
    HIGH = "high", "High"
    MEDIUM = "medium", "Medium"


class Alert(BaseModel):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="alerts"
    )
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="alerts")
    severity = models.CharField(max_length=8, choices=AlertSeverity.choices)
    message = models.CharField(max_length=255)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.severity.upper()} - {self.device.name}"

