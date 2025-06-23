from django import forms
from .models import People

class PeopleForm(forms.ModelForm):
    class Meta:
        model = People
        fields = ['name', 'email', 'phone', 'notes', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Teléfono'}),
            'notes': forms.Textarea(attrs={'placeholder': 'Notas adicionales', 'rows': 3}),
            'type': forms.Select(choices=[
                ('individual', 'Individual'),
                ('company', 'Empresa'),
                ('other', 'Otro')
            ]),
        }