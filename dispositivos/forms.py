# dispositivos/forms.py
from django import forms
from django.utils import timezone
from django.db.models import Q
from .models import Zone, Category, Device, Product, Measurement, Alert

# ------------ Catálogos básicos ------------
class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ["name"]  # organization se setea en la vista


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


# ---------------- Dispositivos ----------------
class DeviceForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.none(),
        required=False,
        label="Productos asociados",
        help_text="Selecciona productos existentes para asociarlos a este dispositivo.",
        widget=forms.SelectMultiple(attrs={"size": 10})
    )

    class Meta:
        model = Device
        fields = ["name", "serial_number", "installed_at", "zone", "organization", "products"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Nombre del dispositivo"}),
            "serial_number": forms.TextInput(attrs={"placeholder": "Serie (opcional)"}),
            "installed_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            base_qs = Product.objects.filter(
                Q(device__isnull=True) | Q(device=self.instance)
            ).select_related("category", "device")
            # valores iniciales: los ya asociados a este device
            self.fields["products"].initial = self.instance.products.values_list("pk", flat=True)
        else:
            base_qs = Product.objects.filter(device__isnull=True).select_related("category", "device")

        self.fields["products"].queryset = base_qs.order_by("name")

    def save(self, commit=True):
        # Guardamos Device primero
        device = super().save(commit=commit)

        # Luego actualizamos los productos asociados
        if "products" in self.cleaned_data:
            selected = list(self.cleaned_data["products"].values_list("pk", flat=True))

            Product.objects.filter(device=device).exclude(pk__in=selected).update(device=None)
            Product.objects.filter(pk__in=selected).update(device=device)

        return device


# ----------------- Productos ------------------
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "model", "serial_number", "device", "category"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Nombre del producto"}),
            "model": forms.TextInput(attrs={"placeholder": "Modelo (opcional)"}),
            "serial_number": forms.TextInput(attrs={"placeholder": "Serie (opcional)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🔸 deja device como opcional
        self.fields["device"].required = False
        self.fields["device"].queryset = Device.objects.select_related("zone").order_by("name")
        self.fields["category"].queryset = Category.objects.order_by("name")


# ---------------- Mediciones ------------------
class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ["product", "value", "unit", "measured_at"]

    def save(self, commit=True):
        obj = super().save(commit)
        # Ya no llamamos a evaluate_measurement_alert aquí
        # La señal post_save se encargará de evaluar y generar eventos
        return obj
# ------------------ Alertas -------------------
class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = ["severity", "message"]

