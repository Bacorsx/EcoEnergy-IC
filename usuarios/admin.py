from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "username", "email", "organization", "role",
        "is_staff", "estado", "created_at"
    )
    list_filter = (
        "organization", "role", "estado",
        "is_staff", "is_superuser", "is_active"
    )
    search_fields = ("username", "email", "organization__name")
    ordering = ("organization", "username")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Información personal", {
            "fields": ("first_name", "last_name", "email", "organization", "role")
        }),
        ("Permisos", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Fechas importantes", {
            "fields": ("last_login", "date_joined", "created_at", "updated_at", "deleted_at")
        }),
        ("Estado lógico", {"fields": ("estado",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "email", "password1", "password2",
                "organization", "role", "estado"
            ),
        }),
    )

    readonly_fields = ("created_at", "updated_at", "deleted_at")
