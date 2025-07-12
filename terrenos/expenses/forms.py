from django import forms
from .models import Expense
from projects.models import Project
from payers.models import Payer
from payment_receivers.models import PaymentReceiver
from expense_types.models import ExpenseType
from expense_type_details.models import ExpenseTypeDetail

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['project', 'date', 'expense_type', 'expense_type_detail', 'amount', 'currency', 'exchange_rate', 'payment_type', 'payer', 'receipt_number', 'receipt', 'accountant', 'accountant_amount', 'accountant_currency', 'payment_receiver', 'notes']
        labels = {
            'project': 'Proyecto',
            'date': 'Fecha de Pago',
            'expense_type': 'Tipo de Gasto',
            'expense_type_detail': 'Detalle de Gasto',
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
            'project': forms.Select(attrs={'class': 'form-control'}, choices=Project.objects.all()),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expense_type': forms.Select(attrs={'class': 'form-control'}, choices=ExpenseType.objects.all()),
            'expense_type_detail': forms.Select(attrs={'class': 'form-control'}, choices=ExpenseTypeDetail.objects.all()),
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
            'payer': forms.Select(attrs={'class': 'form-control'}, choices=Payer.objects.all()),
            'receipt_number': forms.TextInput(attrs={'class': 'form-control'}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
            'accountant': forms.CheckboxInput(),
            'accountant_amount': forms.NumberInput(attrs={'class': 'form-control', 'style':'display: none;'}),
            'accountant_currency': forms.Select(attrs={'class': 'form-control', 'style':'display: none;'}, choices=[
                ('ars', 'Pesos'),
                ('usd', 'Dolares')
            ]),
            'payment_receiver': forms.Select(attrs={'class': 'form-control'}, choices=PaymentReceiver.objects.all()),
            'notes': forms.TextInput(attrs={'class': 'form-control'})

        }
