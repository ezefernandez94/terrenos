from django import forms
from .models import SaleSummary
from sales.models import Sale
from sellers.models import Seller

class SaleSummaryForm(forms.ModelForm):
    class Meta:
        model = SaleSummary
        fields = ['sale', 'amount', 'date', 'type', 'accountant', 'notes', 'exchange_rate', 'seller']
        widgets = {
            'sale': forms.Select(choices=Sale.objects.all()),
            'seller': forms.Select(choices=Seller.objects.all()),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'type': forms.Select(choices=[
                ('sale', 'Venta'),
                ('payment', 'Pago'),
                ('boletus', 'Boletus'),
                ('deed', 'Escritura')
            ]),
            'accountant': forms.CheckboxInput(),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Notas adicionales'})
        }