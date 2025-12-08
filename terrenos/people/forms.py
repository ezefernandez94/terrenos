from django import forms
from .models import People

class PeopleForm(forms.ModelForm):
    class Meta:
        model = People
        fields = ['name', 'email', 'phone', 'notes', 'type']
        labels = {
            'name': 'Nombre Completo',
            'email': 'Mail',
            'phone': 'Teléfono',
            'type': 'Tipo de Contacto',
            'notes': 'Notas'
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nombre completo', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Teléfono', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'placeholder': 'Notas adicionales', 'rows': 3, 'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
        }