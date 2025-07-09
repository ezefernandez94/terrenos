from django.db import models

class PaymentReceiver(models.Model):
    """
    Model representing a payment receiver for land investment.
    """
    name = models.CharField(max_length=100, blank=False, null=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Cobrador"
        verbose_name_plural = "Cobradores"
        ordering = ['name']
