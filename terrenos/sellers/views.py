from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Seller
from .forms import SellerForm

class SellerCreateView(CreateView):
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
    
def index(request):
    """
    Render the index page of the sellers app.
    """
    sellers = Seller.objects.all()
    return render(request, 'sellers/index.html', {"sellers": sellers})

def detail(request, seller_id):
    """
    Render the detail page for a specific seller.
    """
    try:
        seller = Seller.objects.get(id=seller_id)
    except Seller.DoesNotExist:
        raise Http404("<h1>Seller not found</h1>", status=404)
    return render(request, "sellers/detail.html", {"seller": seller})

def create(request):
    """
    Render the create seller page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Seller</h1>")

def edit(request, seller_id):
    """
    Render the edit page for a specific seller.
    """
    # Here you would typically fetch the seller from the database using the seller_id
    # For now, we'll just return a placeholder response
    return HttpResponse(f"<h1>Edit Seller ID: {seller_id}</h1>")

def delete(request, seller_id):
    """
    Render the delete confirmation page for a specific seller.
    """
    # Here you would typically fetch the seller from the database using the seller_id
    # For now, we'll just return a placeholder response
    return HttpResponse(f"<h1>Delete Seller ID: {seller_id}</h1>")

