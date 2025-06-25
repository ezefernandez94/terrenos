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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['person'].required = False  # Always start as not required

        # Handle POST data if present
        data = args[0] if args else None
        if data:
            full_prefix = self.prefix if self.prefix else ''
            field_name = f"{full_prefix}-create_new_person" if full_prefix else "create_new_person"
            create_new_value = data.get(field_name)

            if create_new_value in ["on", "true", "True", True, "1"]:
                # New person will be created — skip requiring person
                self.fields['person'].required = False

    def clean(self):
        cleaned_data = super().clean()
        
        create_new = cleaned_data.get('create_new_person')
        new_name = cleaned_data.get('new_name')
        new_phone = cleaned_data.get('new_phone')

        if create_new:
            
            if not cleaned_data.get('new_name') or not cleaned_data.get('new_phone'):
                raise forms.ValidationError("Debe completar nombre y documento para la nueva persona.")

            # Create or get person here and inject it into cleaned_data
            person, created = People.objects.get_or_create(
                name=new_name,
                phone=new_phone,
                type='buyer'
            )

            cleaned_data['person'] = person
            self.instance.person = person
            print("Person created or retrieved:", person, "Created:", created, "CLeaned Data:", cleaned_data)

        elif not cleaned_data.get('person'):
            raise forms.ValidationError("Debe seleccionar una persona existente o crear una nueva.")
        
        return cleaned_data

    def save(self, commit=True):
        create_new = self.cleaned_data.get('create_new_person')

        if create_new:
            person = People.objects.create(
                name=self.cleaned_data['new_name'],
                phone=self.cleaned_data['new_phone']
            )
            self.instance.person = person

        return super().save(commit=commit)
