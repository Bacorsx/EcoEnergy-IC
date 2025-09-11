from django import forms
from .models import Device, Measurement, Alert

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['category',
                  'zone', 'name', 'model', 
                  'serial_number', 'installed_at'
                ]

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 3:
            raise forms.ValidationError("El nombre del dispositivo debe tener al menos 3 caracteres.")
        return name

class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ['organization','device', 
                  'value', 'measured_at',
                  'unit','estado'
                ]

    def clean_value(self):
        value = self.cleaned_data['value']
        if value < 0:
            raise forms.ValidationError("El valor de la medición no puede ser negativo.")
        return value

class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = ['organization','device', 
                  'severity', 'message', 
                  'is_resolved', 'resolved_at',
                  'estado'
                ]