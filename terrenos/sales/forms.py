from django import forms
from .models import Sale
from people_to_lands.forms import PeopleToLandsForm
from people_to_lands.models import PeopleToLands
from lands.models import Land

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['land', 'sale_date', 'sale_price', 'notes', 'n_payments', 'boletus_date', 'deed_date', 'deed_number']
        widgets = {
            'land': forms.HiddenInput(),
            'sale_date': forms.DateInput(attrs={'type': 'date'}),
            'boletus_date': forms.DateInput(attrs={'type': 'date'}),
            'deed_date': forms.DateInput(attrs={'type': 'date'}),
            'deed_number': forms.TextInput(attrs={'placeholder': 'Número de escritura'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Notas adicionales'})
        }

PeopleToLandFormSet = forms.inlineformset_factory(
    Land,
    PeopleToLands,
    form=PeopleToLandsForm,
    fields=('person', 'land', 'notes'),
    extra=0,
    can_delete=True
)