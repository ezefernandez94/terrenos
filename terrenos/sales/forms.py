from django import forms
from .models import Sale
from people_to_lands.forms import PeopleToLandsForm
from people_to_lands.models import PeopleToLands
from lands.models import Land
from sales_summary.models import SaleSummary

class SaleForm(forms.ModelForm):
    ## Not a Sale field: how the down payment was paid, copied to its 'Pago Inicial' SaleSummary
    down_payment_option = forms.ChoiceField(
        choices=[('', '---------')] + SaleSummary._meta.get_field('payment_option').choices,
        required=False,
        label='Forma de pago del anticipo',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Sale
        fields = ['land', 'sale_date', 'sale_price', 'down_payment', 'down_payment_date', 'n_payments',
                  'boletus_date', 'deed_date', 'deed_number', 'notes']
        labels = {
            'sale_date': 'Fecha de venta',
            'sale_price': 'Precio de venta',
            'down_payment': 'Anticipo',
            'down_payment_date': 'Fecha del anticipo',
            'n_payments': 'Cantidad de cuotas (sobre el saldo)',
            'boletus_date': 'Fecha de boleto',
            'deed_date': 'Fecha de escritura',
            'deed_number': 'Número de escritura',
            'notes': 'Notas',
        }
        help_texts = {
            'down_payment': 'Opcional. Se registra como «Pago Inicial» en el resumen de la venta.',
            'down_payment_date': 'Si se deja vacía se usa la fecha de venta.',
        }
        widgets = {
            'land': forms.HiddenInput(),
            'sale_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'down_payment': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'down_payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'n_payments': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'boletus_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'deed_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'deed_number': forms.TextInput(attrs={'placeholder': 'Número de escritura', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Notas adicionales', 'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ## When editing, show how the existing down payment was recorded
        if self.instance.pk and not self.is_bound:
            summary = self.instance.salesummary_set.filter(type='initial_payment').first()
            if summary:
                self.initial['down_payment_option'] = summary.payment_option

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('sale_price')
        down_payment = cleaned_data.get('down_payment')

        if down_payment is not None:
            if down_payment < 0:
                self.add_error('down_payment', 'El anticipo no puede ser negativo.')
            elif price is not None and down_payment >= price:
                self.add_error('down_payment', 'El anticipo debe ser menor al precio de venta.')
            elif down_payment > 0 and not cleaned_data.get('down_payment_option'):
                self.add_error('down_payment_option', 'Indicá cómo se pagó el anticipo.')
        if cleaned_data.get('n_payments') is not None and cleaned_data['n_payments'] < 0:
            self.add_error('n_payments', 'La cantidad de cuotas no puede ser negativa.')

        return cleaned_data

    def save(self, commit=True):
        sale = super().save(commit=commit)
        if commit:
            sale.sync_down_payment_summary(self.cleaned_data.get('down_payment_option'))
        return sale

PeopleToLandFormSet = forms.inlineformset_factory(
    Land,
    PeopleToLands,
    form=PeopleToLandsForm,
    fields=('person', 'land', 'notes'),
    extra=0,
    can_delete=True
)
