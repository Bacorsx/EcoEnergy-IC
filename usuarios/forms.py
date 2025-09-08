from django import forms
from django.db import transaction
from .models import User
from dispositivos.models import Organization

class SignupForm(forms.ModelForm):
    organization_name = forms.CharField(label="Nombre de empresa", max_length=150)
    email = forms.EmailField(label="Dirección de correo electrónico", required=True)
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "organization_name", "password1", "password2"]

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        # evitar duplicar empresa
        org_name = cleaned.get("organization_name")
        if org_name and Organization.objects.filter(name__iexact=org_name, deleted_at__isnull=True).exists():
            self.add_error("organization_name", "Ya existe una empresa con ese nombre.")
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        # 1) Crear empresa
        org = Organization.objects.create(name=self.cleaned_data["organization_name"])

        # 2) Crear usuario asignado a esa empresa
        user = User(
            username=self.cleaned_data["username"] or self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            organization=org,
        )
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user, org