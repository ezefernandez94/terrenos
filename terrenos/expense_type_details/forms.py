from django import forms
from .models import ExpenseTypeDetail

class ExpenseTypeDetailForm(forms.ModelForm):
    class Meta:
        model = ExpenseTypeDetail
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
