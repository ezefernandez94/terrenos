from django import forms
from .models import INSTALLMENT_PLAN_CHOICES, Project


class InstallmentPlansField(forms.TypedMultipleChoiceField):
    """Checkboxes for Project.installment_plans (an ArrayField of ints)."""

    def __init__(self, **kwargs):
        kwargs.setdefault('label', 'Planes de financiación')
        super().__init__(
            choices=INSTALLMENT_PLAN_CHOICES,
            coerce=int,
            required=False,
            widget=forms.CheckboxSelectMultiple,
            **kwargs,
        )

    def clean(self, value):
        return sorted(super().clean(value))

class ProjectForm(forms.ModelForm):
    installment_plans = InstallmentPlansField(help_text='Se muestran en la web pública: «Tenemos planes de financiación en …».')

    class Meta:
        model = Project
        fields = ['name', 'status', 'start_date', 'end_date', 'installment_plans']
        labels = {
            'name': "Nombre",
            'status': 'Estado',
            'start_date': 'Fecha de Inicio',
            'end_date': 'Fecha de Fin'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'status': forms.Select(attrs={'class':'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class':'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class':'form-control'}),
        }
