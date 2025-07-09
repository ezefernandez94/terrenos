from django.db import models

class Payer(models.Model):
    """
    Model representing a payer for land investment.
    """
    name = models.CharField(max_length=100, blank=False, null=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Pagador"
        verbose_name_plural = "Pagadores"
        ordering = ['name']
