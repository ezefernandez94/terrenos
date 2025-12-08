from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'start_date', 'end_date']
        labels = {
            'name': "Nombre",
            'start_date': 'Fecha de Inicio',
            'end_date': 'Fecha de Fin'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class':'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class':'form-control'}),
        }
