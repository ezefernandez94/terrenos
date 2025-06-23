from django.db import models

class Sale(models.Model):
    """
    Model representing a sale of a land plot.
    """
    land = models.ForeignKey('lands.Land', on_delete=models.CASCADE)
    sale_date = models.DateField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    n_payments = models.IntegerField(default=1)
    boletus_date = models.DateField(blank=True, null=True)
    deed_date = models.DateField(blank=True, null=True)
    deed_number = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Sale of {self.land} to {self.buyer} on {self.sale_date}"

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['sale_date']