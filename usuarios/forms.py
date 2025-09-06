from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Organization

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(), required=False, empty_label="(Sin organización)"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "organization")
        