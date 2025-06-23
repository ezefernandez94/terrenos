from django.db import models

class Seller(models.Model):
    """
    Model representing a seller of land plots.
    """
    name = models.CharField(max_length=100, blank=False, null=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"
        ordering = ['name']