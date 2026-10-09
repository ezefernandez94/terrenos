from django import forms
from people.models import People
from .models import PeopleToLands

class PeopleToLandsForm(forms.ModelForm):
    create_new_person = forms.BooleanField(required=False, label='Agregar nueva persona')

    new_name = forms.CharField(required=False, label='Nombre')
    new_phone = forms.CharField(required=False, label='Teléfono')

    class Meta:
        model = PeopleToLands
        fields = ['person', 'notes']
        widgets = {
            'person': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ## Either an existing person or a new one is required; clean() enforces it
        self.fields['person'].required = False
        self.fields['new_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_phone'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('create_new_person'):
            ## Only the name is required; the phone can be completed later
            if not cleaned_data.get('new_name'):
                self.add_error('new_name', "Ingresá el nombre de la nueva persona.")
        elif not cleaned_data.get('person'):
            self.add_error('person', "Seleccioná una persona existente o marcá «Agregar nueva persona».")

        return cleaned_data

    def save(self, commit=True):
        ## The person is created here and not in clean(), so a failed form leaves no orphan rows
        if self.cleaned_data.get('create_new_person'):
            self.instance.person = People.objects.create(
                name=self.cleaned_data['new_name'],
                phone=self.cleaned_data.get('new_phone') or None,
                type='buyer',
            )

        return super().save(commit=commit)
