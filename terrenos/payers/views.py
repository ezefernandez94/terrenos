from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from .models import Payer
from .forms import PayerForm
from django.contrib.auth.decorators import login_required

class PayerCreateView(CreateView):
    """
    View to create a new payer.
    """
    model = Payer
    form_class = PayerForm
    template_name = 'payers/create.html'
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('payers:index')
    
    def form_valid(self, form):
        return super().form_valid(form)
    
class PayerDeleteView(DeleteView):
    """
    View to delete a payer.
    """
    model = Payer
    template_name = 'payers/delete.html'
    success_url = reverse_lazy('payers:index')
    
@login_required
def index(request):
    """
    Render the index page of the payers app.
    """
    payers = Payer.objects.all()
    return render(request, 'payers/index.html', {"payers": payers})

@login_required
def detail(request, payer_id):
    """
    Render the detail page for a specific payer.
    """
    try:
        payer = Payer.objects.get(id=payer_id)
    except Payer.DoesNotExist:
        raise Http404("<h1>Payer not found</h1>", status=404)
    return render(request, "payers/detail.html", {"payer": payer})

@login_required
def create(request):
    """
    Render the create payer page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Payer</h1>")

@login_required
def edit(request, payer_id):
    """
    Render the edit page for a specific payer.
    """
    payer = get_object_or_404(Payer, pk=payer_id)
    if request.method == 'POST':
        form = PayerForm(request.POST, instance=payer)
        if form.is_valid():
            form.save()
            return render(request, 'payers/detail.html', {"payer": payer})
    else:
        form = PayerForm(instance=payer)
    return render(request, 'payers/edit.html', {'form': form})

@login_required
def delete(request, payer_id):
    """
    Render the delete confirmation page for a specific payer.
    """
    payer = get_object_or_404(Payer, pk=payer_id)
    if request.method == 'POST':
        payer.delete()
        return HttpResponse("<h1>Payer deleted successfully</h1>")
    
    return render(request, 'payers/delete.html', {'payer': payer})
