from django import forms
from .models import ExpenseTypeDetail

class ExpenseTypeDetailForm(forms.ModelForm):
    class Meta:
        model = ExpenseTypeDetail
        fields = ['description', 'notes']
        labels = {
            'description': 'Descripción',
            'notes': 'Notas'
        }
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'})
        }
