from django import forms
from .models import PaymentReceiver

class PaymentReceiverForm(forms.ModelForm):
    class Meta:
        model = PaymentReceiver
        fields = ['name', 'notes']