from django import forms
from .models import SaleSummary
from sellers.models import Seller

class SaleSummaryForm(forms.ModelForm):
    class Meta:
        model = SaleSummary
        fields = ['sale', 'amount', 'date', 'type', 'payment_option', 'accountant', 'notes', 'exchange_rate', 'seller']
        widgets = {
            'sale': forms.HiddenInput(),
            'seller': forms.Select(choices=Seller.objects.all()),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'type': forms.Select(choices=[
                ('initial_payment', 'Pago Inicial'),
                ('monthly_payment', 'Cuota'),
                ('remaining_payment', 'Pago de Saldo Restante')
            ]),
            'payment_option': forms.Select(choices=[
                ('pesos', 'Pesos'),
                ('usd', 'Dolares'),
                ('cheque', 'Cheque'),
                ('tranfer', 'Tranferencia')
            ]),
            'accountant': forms.CheckboxInput(),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Notas adicionales'})
        }