from django import forms
from .models import ExpenseType

class ExpenseTypeForm(forms.ModelForm):
    class Meta:
        model = ExpenseType
        fields = ['description', 'key', 'notes']
        labels = {
            'description': 'Descripción',
            'key': 'Clave',
            'notes': 'Notas'
        }
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'})
        }
