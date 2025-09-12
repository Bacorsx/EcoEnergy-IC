# core/models.py
from django.db import models
from django.utils import timezone

# ---------------------------
# QuerySet con soft delete
# ---------------------------
class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        # Soft delete en lote
        return super().update(deleted_at=timezone.now(), estado="INACTIVO")

    def hard_delete(self):
        # Borrado físico 
        return super().delete()

    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)


# ---------------------------
# Managers
# ---------------------------
class SoftDeleteManager(models.Manager):
    """Manager por defecto: solo registros vivos."""
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    # Accesos convenientes
    def with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

    def only_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db).dead()


class AllObjectsManager(models.Manager):
    """Manager alterno: incluye vivos y eliminados (auditoría/hard_delete)."""
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


# ---------------------------
# BaseModel con timestamps + soft delete
# ---------------------------
class BaseModel(models.Model):
    ESTADOS = (("ACTIVO", "Activo"), ("INACTIVO", "Inactivo"))

    estado = models.CharField(max_length=10, choices=ESTADOS, default="ACTIVO")
    created_at = models.DateTimeField(auto_now_add=True)   # creación
    updated_at = models.DateTimeField(auto_now=True)       # actualización
    deleted_at = models.DateTimeField(null=True, blank=True)  # soft delete

    # Managers
    objects = SoftDeleteManager()      # por defecto: vivos
    all_objects = AllObjectsManager()  # incluye eliminados

    class Meta:
        abstract = True

    # Soft delete individual
    def delete(self, using=None, keep_parents=False):
        if self.deleted_at:
            return  # ya estaba eliminado
        self.deleted_at = timezone.now()
        self.estado = "INACTIVO"
        self.save(update_fields=["deleted_at", "estado", "updated_at"])

    # Borrado físico individual
    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)


# ---------------------------
# Organization
# ---------------------------
class Organization(BaseModel):
    name = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        db_table = "organizations"
        indexes = [
            models.Index(fields=["name"]),
        ]
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"

    def __str__(self):
        return self.name
