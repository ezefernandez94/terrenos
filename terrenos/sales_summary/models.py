from django.db import models
import requests

class SaleSummary(models.Model):
    """
    Model representing a summary of sales for a specific land plot.
    """
    sale = models.ForeignKey('sales.Sale', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    type = models.CharField(
        max_length=50,
        choices=[
            ('initial_payment', 'Pago Inicial'),
            ('monthly_payment', 'Cuota'),
            ('remaining_payment', 'Pago de Saldo Restante')
        ],
        ## Was 'sale', which is not one of the choices
        default='monthly_payment'
    )
    payment_option = models.CharField(
        max_length=50,
        choices=[
            ('pesos', 'Pesos'),
            ('usd', 'Dolares'),
            ('cheque', 'Cheque'),
            ('tranfer', 'Tranferencia')
        ]
    )
    accountant = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4)
    seller = models.ForeignKey(
        'sellers.Seller',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Summary for {self.sale}"
    
    def save(self, *args, **kwargs):
        if not self.exchange_rate:
            ## Search USD value from an API; a network failure must not block saving the payment
            try:
                response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
                response.raise_for_status()
                self.exchange_rate = response.json()['rates'].get('ARS', 1.0)
            except (requests.RequestException, ValueError, KeyError):
                self.exchange_rate = 1.0
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Resumen de Ventas"
        verbose_name_plural = "Resumenes de Ventas"
        ordering = ['date']