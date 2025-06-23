from django import forms
from .models import Land
from projects.models import Project
from sellers.models import Seller

class LandForm(forms.ModelForm):
    class Meta:
        model = Land
        fields = ['project', 'manual_id', 'block', 'size', 'type', 'price', 'status', 'notes', 'seller']
        widgets = {
            'project': forms.Select(choices=Project.objects.all()),
            'type': forms.Select(choices=[
                ('maintenance', 'Mantenimiento'),
                ('utilities', 'Servicios'),
                ('taxes', 'Impuestos'),
                ('other', 'Otro')
            ]),
            'seller': forms.ModelChoiceField(queryset=Seller.objects.all(), empty_label="Seleccione un vendedor")
        }
