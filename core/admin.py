from django.contrib import admin
from .models import Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "estado", "created_at")
    search_fields = ("name", "email")
    list_filter = ("estado",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    # evita que los timestamps aparezcan como editables
    fieldsets = (
        (None, {"fields": ("name", "email", "estado")}),
        ("Timestamps", {"fields": ("created_at", "updated_at", "deleted_at")}),
    )
