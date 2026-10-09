from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from .models import Seller
from .forms import SellerForm
from django.contrib.auth.decorators import login_required

class SellerCreateView(LoginRequiredMixin, CreateView):
    """
    View to create a new seller.
    """
    model = Seller
    form_class = SellerForm
    template_name = 'sellers/create.html'
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('sellers:index')
    
    def form_valid(self, form):
        return super().form_valid(form)
    
class SellerDeleteView(LoginRequiredMixin, DeleteView):
    """
    View to delete a seller.
    """
    model = Seller
    template_name = 'sellers/delete.html'
    success_url = reverse_lazy('sellers:index')
    
@login_required
def index(request):
    """
    Render the index page of the sellers app.
    """
    sellers = Seller.objects.all()
    return render(request, 'sellers/index.html', {"sellers": sellers})

@login_required
def detail(request, seller_id):
    """
    Render the detail page for a specific seller.
    """
    try:
        seller = Seller.objects.get(id=seller_id)
    except Seller.DoesNotExist:
        raise Http404("<h1>Seller not found</h1>", status=404)
    return render(request, "sellers/detail.html", {"seller": seller})

@login_required
def create(request):
    """
    Render the create seller page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Seller</h1>")

@login_required
def edit(request, seller_id):
    """
    Render the edit page for a specific seller.
    """
    seller = get_object_or_404(Seller, pk=seller_id)
    if request.method == 'POST':
        form = SellerForm(request.POST, instance=seller)
        if form.is_valid():
            form.save()
            return render(request, 'sellers/detail.html', {"seller": seller})
    else:
        form = SellerForm(instance=seller)
    return render(request, 'sellers/edit.html', {'form': form})

@login_required
def delete(request, seller_id):
    """
    Render the delete confirmation page for a specific seller.
    """
    seller = get_object_or_404(Seller, pk=seller_id)
    if request.method == 'POST':
        ## Land.seller is SET_NULL: the lands stay, they just lose who sold them
        seller.delete()
        messages.success(request, 'Vendedor eliminado.')
        return redirect('sellers:index')

    lands = seller.land_set.select_related('project').order_by('project__name', 'block', 'manual_id')
    return render(request, 'sellers/delete.html', {'seller': seller, 'lands': lands})
