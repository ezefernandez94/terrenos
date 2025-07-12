from django.db import models

class ExpenseTypeDetail(models.Model):
    """
    Model representing a expense type detail
    """
    description = models.TextField(blank=True, null=True)
    key = models.CharField(max_length=100, unique=True, null=False, blank=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Detalle de Tipo de Gasto: {self.description} ({self.notes})"

    class Meta:
        verbose_name = "Detalle de Tipo de Gasto"
        verbose_name_plural = "Detalles de Tipos de Gasto"
        ordering = ['description']