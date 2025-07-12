from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from .models import PaymentReceiver
from .forms import PaymentReceiverForm
from django.contrib.auth.decorators import login_required

class PaymentReceiverCreateView(CreateView):
    """
    View to create a new payment receiver.
    """
    model = PaymentReceiver
    form_class = PaymentReceiverForm
    template_name = 'payment_receivers/create.html'
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('payment_receivers:index')
    
    def form_valid(self, form):
        return super().form_valid(form)
    
class SellerDeleteView(DeleteView):
    """
    View to delete a payment receiver.
    """
    model = PaymentReceiver
    template_name = 'payment_receivers/delete.html'
    success_url = reverse_lazy('payment_receivers:index')
    
@login_required
def index(request):
    """
    Render the index page of the payment receiver app.
    """
    payment_receivers = PaymentReceiver.objects.all()
    return render(request, 'payment_receivers/index.html', {"payment_receivers": payment_receivers})

@login_required
def detail(request, payment_receiver_id):
    """
    Render the detail page for a specific payment receiver.
    """
    try:
        payment_receiver = PaymentReceiver.objects.get(id=payment_receiver_id)
    except PaymentReceiver.DoesNotExist:
        raise Http404("<h1>Cobrador no encontrado</h1>", status=404)
    return render(request, "payment_receivers/detail.html", {"receiver": payment_receiver})

@login_required
def create(request):
    """
    Render the create payment receiver page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Payment Receiver</h1>")

@login_required
def edit(request, payment_receiver_id):
    """
    Render the edit page for a specific payment receiver.
    """
    payment_receiver = get_object_or_404(PaymentReceiver, pk=payment_receiver_id)
    if request.method == 'POST':
        form = PaymentReceiverForm(request.POST, instance=payment_receiver)
        if form.is_valid():
            form.save()
            return render(request, 'payment_receivers/detail.html', {"receiver": payment_receiver})
    else:
        form = PaymentReceiverForm(instance=payment_receiver)
    return render(request, 'payment_receivers/edit.html', {'form': form})

@login_required
def delete(request, payment_receiver_id):
    """
    Render the delete confirmation page for a specific payment receiver.
    """
    payment_receiver = get_object_or_404(PaymentReceiver, pk=payment_receiver_id)
    if request.method == 'POST':
        payment_receiver.delete()
        return HttpResponse("<h1>Cobrador eliminado exitosamente</h1>")
    
    return render(request, 'payment_receivers/delete.html', {'receiver': payment_receiver})
