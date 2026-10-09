from django.db import models

class Sale(models.Model):
    """
    Model representing a sale of a land plot.
    """
    land = models.ForeignKey('lands.Land', on_delete=models.CASCADE)
    sale_date = models.DateField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    ## Paid up front (same currency as sale_price); n_payments covers only the remainder
    down_payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    down_payment_date = models.DateField(blank=True, null=True)
    n_payments = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pendiente'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ], default='pending')
    boletus_date = models.DateField(blank=True, null=True)
    deed_date = models.DateField(blank=True, null=True)
    deed_number = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Sale of {self.land} on {self.sale_date}"

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['sale_date']

    @property
    def is_paid(self):
        """
        Check if the sale is fully paid.
        """
        return self.status == 'completed'

    @property
    def financed_amount(self):
        """
        Amount left to pay in installments after the down payment.
        """
        return self.sale_price - (self.down_payment or 0)

    @property
    def installment_amount(self):
        """
        Value of each installment, or None when there are no installments.
        """
        if not self.n_payments or self.n_payments < 1:
            return None
        return round(self.financed_amount / self.n_payments, 2)

    def sync_down_payment_summary(self, payment_option):
        """
        Create or update the 'Pago Inicial' SaleSummary that records the down payment.
        A summary is never deleted here: if the down payment is removed it may still be a real payment.
        """
        from sales_summary.models import SaleSummary

        if not self.down_payment:
            return None
        summary = self.salesummary_set.filter(type='initial_payment').first() or SaleSummary(
            sale=self,
            type='initial_payment',
            notes='Generado automáticamente al registrar la venta.',
        )
        summary.amount = self.down_payment
        summary.date = self.down_payment_date or self.sale_date
        summary.payment_option = payment_option
        summary.save()
        return summary