from django.db import models

class ExpenseType(models.Model):
    """
    Model representing a expense type
    """
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Tipo de Gasto: {self.description} ({self.notes})"

    class Meta:
        verbose_name = "Tipo de Gasto"
        verbose_name_plural = "Tipos de Gasto"
        ordering = ['description']