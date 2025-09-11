from django.contrib import admin
from .models import Organization, Zone, Category, Device, Measurement, Alert

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "estado", "created_at")
    search_fields = ("name", "email")
    list_filter = ("estado",)

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "estado", "created_at")
    search_fields = ("name",)
    list_filter = ("organization", "estado")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "estado", "created_at")
    search_fields = ("name",)
    list_filter = ("organization", "estado")

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "category", "zone", "serial_number", "estado")
    search_fields = ("name", "serial_number")
    list_filter = ("organization", "category", "zone", "estado")

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ("device", "value", "unit", "measured_at", "organization")
    list_filter = ("organization", "device", "unit")
    search_fields = ("device__name",)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("device", "severity", "is_resolved", "created_at", "organization")
    list_filter = ("organization", "severity", "is_resolved", "estado")
    search_fields = ("device__name", "message")
