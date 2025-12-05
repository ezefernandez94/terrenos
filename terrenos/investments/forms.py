from django import forms
from .models import Investment

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['project', 'date', 'expense_type', 'expense_type_detail', 'amount', 'currency', 'exchange_rate', 'payment_type', 'payer', 'receipt_number', 'accountant', 'accountant_amount', 'accountant_currency', 'payment_receiver', 'notes']
        labels = {
            'project': 'Proyecto',
            'date': 'Fecha de Pago',
            'expense_type': 'Tipo de Inversión',
            'expense_type_detail': 'Detalle de Inversión',
            'amount': 'Valor',
            'currency': 'Moneda',
            'exchange_rate': 'Tasa de Cambio',
            'payment_type': 'Tipo de Pago',
            'payer': 'Pagó',
            'receipt_number': 'Número de Comprobante',
            'accountant': 'Contable?',
            'accountant_amount': 'Monto Contable',
            'accountant_currency': 'Moneda Contable',
            'payment_receiver': 'Se pago a',
            'notes': 'Notas'
        }
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'expense_type': forms.Select(attrs={'class': 'form-control'}),
            'expense_type_detail': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('ars', 'Pesos'),
                ('usd', 'Dolares')
            ]),
            'exchange_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_type': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('cash', 'Efectivo'),
                ('transfer', 'Transferencia'),
                ('cheque', 'Cheque'),
                ('debit_card', 'tarjeta de Débito'),
                ('credit_card', 'Tarjeta de Cédito'),
                ('other', 'Otro')
            ]),
            'payer': forms.Select(attrs={'class': 'form-control'}),
            'receipt_number': forms.TextInput(attrs={'class': 'form-control'}),
            'accountant': forms.CheckboxInput(),
            'accountant_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'accountant_currency': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('ars', 'Pesos'),
                ('usd', 'Dolares')
            ]),
            'payment_receiver': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'})

        }
