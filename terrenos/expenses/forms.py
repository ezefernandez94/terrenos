from django import forms
from .models import Expense
from projects.models import Project
from sellers.models import Seller

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['project', 'date', 'amount', 'detail', 'type', 'receipt_number', 'accountant', 'notes', 'exchange_rate', 'seller']
        widgets = {
            'project': forms.Select(choices=Project.objects.all()),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'type': forms.Select(choices=[
                ('maintenance', 'Mantenimiento'),
                ('utilities', 'Servicios'),
                ('taxes', 'Impuestos'),
                ('other', 'Otro')
            ]),
            'accountant': forms.CheckboxInput(),
            'seller': forms.Select(choices=Seller.objects.all())
        }
