# dispositivos/admin.py
from django.contrib import admin
from django import forms
from django.db import models
from django.utils import timezone

from .models import (
    Zone, Category, Device, Product, Measurement,
    Alert, ProductAlert, ProductAlertEvent
)

# ---------- Device: form con selector de productos ----------
class DeviceAdminForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.none(),
        required=False,
        label="Productos a asociar",
        help_text="Selecciona productos sin dispositivo o ya asociados a este.",
        widget=admin.widgets.FilteredSelectMultiple("Productos", is_stacked=False),
    )

    class Meta:
        model = Device
        fields = ["name", "serial_number", "installed_at", "zone", "organization", "products"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            base_qs = Product.objects.filter(
                models.Q(device__isnull=True) | models.Q(device=self.instance)
            ).select_related("device", "category")
            # preseleccionar los ya asociados
            self.fields["products"].initial = self.instance.products.values_list("pk", flat=True)
        else:
            base_qs = Product.objects.filter(
                device__isnull=True
            ).select_related("device", "category")

        self.fields["products"].queryset = base_qs.order_by("name")


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    form = DeviceAdminForm
    list_display = ("name", "serial_number", "zone", "organization", "estado", "created_at")
    list_filter  = ("zone", "organization", "estado")
    search_fields = ("name", "serial_number")
    fieldsets = (
        (None, {
            "fields": (
                "estado", "deleted_at",
                "name", "serial_number", "installed_at",
                "zone", "organization",
                "products",  # el selector múltiple
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        # Guarda primero el device (para tener pk)
        super().save_model(request, obj, form, change)
        # Sincroniza productos seleccionados DESPUÉS de guardar
        if "products" in form.cleaned_data:
            selected_ids = list(form.cleaned_data["products"].values_list("pk", flat=True))
            # Quita los que ya no están marcados
            Product.objects.filter(device=obj).exclude(pk__in=selected_ids).update(device=None)
            # Asocia los marcados
            Product.objects.filter(pk__in=selected_ids).update(device=obj)


# ---------- Inlines para gestionar rangos por producto ----------
class ProductAlertInline(admin.TabularInline):
    model = ProductAlert
    extra = 3  # normalmente crearás GRAVE, ALTO, MEDIANO
    fields = ("alert", "range_min", "range_max", "unit")
    autocomplete_fields = ("alert",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "device", "category", "serial_number", "estado")
    list_filter  = ("category", "device", "estado")
    search_fields = ("name", "serial_number")
    inlines = [ProductAlertInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "estado")
    search_fields = ("name",)


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "estado")
    list_filter = ("organization",)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    # La resolución está en ProductAlertEvent, no aquí
    list_display = ("severity", "message", "created_at")
    list_filter  = ("severity",)
    search_fields = ("severity","message",)


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ("product", "value", "unit", "measured_at", "triggered_alerts")
    list_filter  = ("unit", "product__device")
    search_fields = ("product__name",)

    def triggered_alerts(self, obj):
        severities = [
            e.product_alert.alert.get_severity_display()
            for e in obj.alert_events.select_related("product_alert__alert")
        ]
        return ", ".join(severities) if severities else "—"
    triggered_alerts.short_description = "Alertas disparadas"


@admin.register(ProductAlert)
class ProductAlertAdmin(admin.ModelAdmin):
    list_display = ("product", "alert", "range_min", "range_max", "unit", "estado")
    list_filter = ("alert__severity", "unit", "estado")
    search_fields = ("product__name",)


@admin.register(ProductAlertEvent)
class ProductAlertEventAdmin(admin.ModelAdmin):
    list_display = ("product_name", "device_name", "alert_severity", "value_with_unit", "measured_at", "is_resolved", "created_at")
    list_filter = ("product_alert__alert__severity", "is_resolved")
    search_fields = ("product_alert__product__name", "measurement__product__name")

    @admin.display(description="Producto")
    def product_name(self, obj):
        return obj.product_alert.product.name

    @admin.display(description="Dispositivo")
    def device_name(self, obj):
        dev = obj.product_alert.product.device
        return dev.name if dev else "—"

    @admin.display(description="Severidad")
    def alert_severity(self, obj):
        return obj.product_alert.alert.get_severity_display()

    @admin.display(description="Valor")
    def value_with_unit(self, obj):
        m = obj.measurement
        return f"{m.value} {m.unit}"

    @admin.display(description="Medido en")
    def measured_at(self, obj):
        return obj.measurement.measured_at

    @admin.action(description="Marcar seleccionadas como resueltas")
    def marcar_resueltas(self, request, queryset):
        updated = queryset.update(is_resolved=True, resolved_at=timezone.now())
        self.message_user(request, f"{updated} evento(s) marcados como resueltos.")
    actions = ["marcar_resueltas"]
