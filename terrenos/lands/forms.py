from django import forms
from .models import Land
from projects.models import Project
from sellers.models import Seller

class LandForm(forms.ModelForm):
    class Meta:
        model = Land
        fields = ['manual_id', 'block', 'width', 'length', 'type', 'price', 'status', 'notes', 'seller']
        exclude = ['project']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('maintenance', 'Mantenimiento'),
                ('utilities', 'Servicios'),
                ('expenses', 'Impuestos'),
                ('other', 'Otro')
            ]),
            'seller': forms.Select(attrs={'class': 'form-control'})
        }
