from django.db import models

class ExpenseType(models.Model):
    """
    Model representing a expense type
    """
    description = models.TextField(blank=True, null=True)
    key = models.CharField(max_length=100, unique=True, null=False, blank=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Concepto de Inversión: {self.description}"

    class Meta:
        verbose_name = "Concepto de Inversión"
        verbose_name_plural = "Conceptos de Inversión"
        ordering = ['description']