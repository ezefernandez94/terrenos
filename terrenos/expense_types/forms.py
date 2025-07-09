from django import forms
from .models import ExpenseType

class ExpenseTypeForm(forms.ModelForm):
    class Meta:
        model = ExpenseType
        fields = ['description', 'notes']
        labels = {
            'description': 'Descripción',
            'notes': 'Notas'
        }
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'})
        }
