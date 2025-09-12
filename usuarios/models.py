from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import BaseModel, Organization  # ✅ Importa desde core

class User(AbstractUser, BaseModel):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="users",
        null=True, blank=True
    )
    role = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "usuarios_user"
        constraints = [
            models.UniqueConstraint(fields=["organization", "username"], name="uq_user_org_username"),
        ]
        indexes = [models.Index(fields=["organization"])]

    def __str__(self):
        return self.username
