from django.db import models
from django.contrib.auth.models import AbstractUser


# 🔹 Modelo base para herencia
class BaseModel(models.Model):
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Organization(BaseModel):
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)

    class Meta:
        db_table = "organizations"

    def __str__(self):
        return self.name


class User(AbstractUser, BaseModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.username
