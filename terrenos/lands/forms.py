from django import forms
from .models import Land

class LandForm(forms.ModelForm):
    class Meta:
        model = Land
        fields = ['project', 'manual_id', 'block', 'width', 'length', 'type', 'price', 'currency', 'status', 'seller', 'notes']
        labels = {
            'project': 'Proyecto',
            'manual_id': 'ID Terreno',
            'block': 'Manzana',
            'width': 'Ancho',
            'length': 'Largo',
            'type': 'Tipo',
            'price': 'Precio',
            'currency': 'Modeda',
            'status': 'Estado',
            'seller': 'Vendió',
            'notes': 'Notas'
        }
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'manual_id': forms.TextInput(attrs={'class': 'form-control'}),
            'block': forms.TextInput(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control'}),
            'length': forms.NumberInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'seller': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control'})
        }
