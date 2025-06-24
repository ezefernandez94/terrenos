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
            'project': forms.Select(choices=Project.objects.all()),
            'type': forms.Select(choices=[
                ('maintenance', 'Mantenimiento'),
                ('utilities', 'Servicios'),
                ('taxes', 'Impuestos'),
                ('other', 'Otro')
            ]),
            'seller': forms.Select(choices=Seller.objects.all())
        }
