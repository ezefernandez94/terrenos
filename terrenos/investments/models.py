from django.db import models
import requests

class Investment(models.Model):
    """
    Model representing an investment related to a project
    """
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    date = models.DateField()
    type = models.ForeignKey('expense_types.ExpenseType', on_delete=models.CASCADE)
    detail = models.ForeignKey('expense_type_details.ExpenseTypeDetail', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=[
        ('ars', 'Pesos'),
        ('usd', 'Dolares')
    ])
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4)
    payment_type = models.CharField(max_length=20, choices=[
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia'),
        ('cheque', 'Cheque'),
        ('debit_card', 'tarjeta de Débito'),
        ('credit_card', 'Tarjeta de Cédito'),
        ('other', 'Otro')
    ])
    payer = models.ForeignKey(
        'payers.Payer',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    receipt_number = models.CharField(max_length=20, blank=True, null=True)
    accountant = models.BooleanField(default=False)
    accountant_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    accountant_currency = models.CharField(max_length=3, choices=[
        ('ars', 'Pesos'),
        ('usd', 'Dolares')
    ], blank=True, null=True)
    payment_receiver = models.ForeignKey(
        'payment_receivers.PaymentReceiver',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Investment for {self.land.manual_id} on {self.date}"

    def save(self, *args, **kwargs):
        if not self.exchange_rate:
            ## Search USD value from an API
            response = requests.get("https://dolarapi.com/v1/dolares/blue")
            if response.status_code == 200:
                data = response.json()
                self.exchange_rate = data['compra']
            else:
                self.exchange_rate = 0.0
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Inversión"
        verbose_name_plural = "Inversiones"
        ordering = ['date']