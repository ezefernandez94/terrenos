from django import forms
from .models import Sale
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