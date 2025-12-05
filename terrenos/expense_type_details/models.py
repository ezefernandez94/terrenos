from django.db import models

class ExpenseTypeDetail(models.Model):
    """
    Model representing a expense type detail
    """
    description = models.TextField(blank=True, null=True)
    key = models.CharField(max_length=100, unique=True, null=False, blank=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Detalle de Tipo de Gasto: {self.description}"

    class Meta:
        verbose_name = "Detalle de Inversión"
        verbose_name_plural = "Detalles de Inversióon"
        ordering = ['description']