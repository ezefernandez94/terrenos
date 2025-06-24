from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import CreateView,DeleteView
from django.urls import reverse_lazy
from .models import Sale
from .forms import SaleForm
from lands.models import Land

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

class SaleDeleteView(DeleteView):
    """
    View to delete a sale.
    """
    model = Sale
    template_name = 'sales/delete.html'
    success_url = reverse_lazy('sales:index')

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
    sale = get_object_or_404(Sale, pk=sale_id)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            return render(request, 'sales/detail.html', {"sale": sale})
    else:
        form = SaleForm(instance=sale)
    return render(request, 'sales/edit.html', {'form': form})


def delete(request, sale_id):
    """
    Render the delete confirmation page for a specific sale.
    """
    sale = get_object_or_404(Sale, pk=sale_id)
    if request.method == 'POST':
        sale.delete()
        return HttpResponse("<h1>Sale deleted successfully</h1>")
    
    return render(request, 'sales/delete.html', {'sale': sale})

def sell_land(request, land_id):
    """
    Render the page to sell a specific land.
    """
    land = get_object_or_404(Land, pk=land_id)

    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save()
            # Optional: mark land as sold
            land.status = 'sold'
            land.save()
            return render(request, 'sales/detail.html', {"sale": sale})
    else:
        form = SaleForm(initial={'land': land})

    return render(request, 'sales/sell_land.html', {
        'form': form,
        'land': land
    })