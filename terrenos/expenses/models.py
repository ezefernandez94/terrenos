from django.db import models
import requests

class Expense(models.Model):
    """
    Model representing an expense related to a project
    """
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    detail = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50, choices=[
        ('maintenance', 'Mantenimiento'),
        ('utilities', 'Servicios'),
        ('taxes', 'Impuestos'),
        ('other', 'Otro')
    ])
    receipt_number = models.CharField(max_length=20, blank=True, null=True)
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
        return f"Expense for {self.land.manual_id} on {self.date}"

    def save(self, *args, **kwargs):
        if not self.exchange_rate:
            ## Search USD value from an API
            response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
            if response.status_code == 200:
                data = response.json()
                self.exchange_rate = data['rates'].get('ARS', 1.0)
            else:
                self.exchange_rate = 1.0
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ['date']