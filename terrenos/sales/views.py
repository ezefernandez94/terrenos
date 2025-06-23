from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Sale
from .forms import SaleForm

class SaleCreateView(CreateView):
    """
    View to create a new sale.
    """
    model = Sale
    form_class = SaleForm
    template_name = 'sales/create.html'
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('sales:index')
    
    def form_valid(self, form):
        return super().form_valid(form)
    
def index(request):
    """
    Render the index page of the sales app.
    """
    sales = Sale.objects.all()
    return render(request, 'sales/index.html', {"sales": sales})

def detail(request, sale_id):
    """
    Render the detail page for a specific sale.
    """
    try:
        sale = Sale.objects.get(id=sale_id)
    except Sale.DoesNotExist:
        raise Http404("<h1>Sale not found</h1>", status=404)
    return render(request, "sales/detail.html", {"sale": sale})

def create(request):
    """
    Render the create sale page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Sale</h1>")

def edit(request, sale_id):
    """
    Render the edit page for a specific sale.
    """
    # Here you would typically fetch the sale from the database using the sale_id
    # For now, we'll just return a placeholder response
    return HttpResponse(f"<h1>Edit Sale ID: {sale_id}</h1>")

def delete(request, sale_id):
    """
    Render the delete confirmation page for a specific sale.
    """
    # Here you would typically fetch the sale from the database using the sale_id
    # For now, we'll just return a placeholder response
    return HttpResponse(f"<h1>Delete Sale ID: {sale_id}</h1>")

