from django import forms
from .models import Seller
from sales.models import Sale
from sellers.models import Seller

class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['name', 'notes']