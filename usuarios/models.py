from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import BaseModel


class User(AbstractUser, BaseModel):
    organization = models.ForeignKey(
        'dispositivos.Organization', on_delete=models.CASCADE, related_name="users",
        null=True, blank=True
    )
    role = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "usuarios_user"
        constraints = [
            # username único por organización (permite mismo username en tenants distintos)
            models.UniqueConstraint(fields=["organization", "username"], name="uq_user_org_username"),
        ]
        indexes = [models.Index(fields=["organization"])]

    def __str__(self):
        return self.username
