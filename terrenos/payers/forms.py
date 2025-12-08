from django import forms
from .models import Payer

class PayerForm(forms.ModelForm):
    class Meta:
        model = Payer
        fields = ['name', 'notes']
        labels = {
            'name': 'Nombre Completo',
            'notes': 'Notas'
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nombre completo', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'placeholder': 'Notas', 'rows': 3, 'class': 'form-control'})
        }