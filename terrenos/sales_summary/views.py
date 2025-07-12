from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from .models import SaleSummary
from .forms import SaleSummaryForm
from sales.models import Sale
from django.contrib.auth.decorators import login_required

class SaleSummaryCreateView(CreateView):
    """
    View to create a new sale_summary.
    """
    model = SaleSummary
    form_class = SaleSummaryForm
    template_name = 'sales_summary/create.html'
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('sales_summary:index')
    
    def form_valid(self, form):
        return super().form_valid(form)
    
class SaleSummaryDeleteView(DeleteView):
    """
    View to delete a seller.
    """
    model = SaleSummary
    template_name = 'sales_summary/delete.html'
    success_url = reverse_lazy('sales_summary:index')

@login_required
def index(request):
    """
    Render the index page of the sales_summary app.
    """
    sales_summary = SaleSummary.objects.all()
    return render(request, 'sales_summary/index.html', {"sales_summary": sales_summary})

@login_required
def detail(request, sale_summary_id):
    """
    Render the detail page for a specific sale_summary.
    """
    try:
        sale_summary = SaleSummary.objects.get(id=sale_summary_id)
    except SaleSummary.DoesNotExist:
        raise Http404("<h1>SaleSummary not found</h1>", status=404)
    return render(request, "sales_summary/detail.html", {"sale_summary": sale_summary})

@login_required
def create(request):
    """
    Render the create sale_summary page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New SaleSummary</h1>")

@login_required
def edit(request, sale_summary_id):
    """
    Render the edit page for a specific seller.
    """
    sale_summary = get_object_or_404(SaleSummary, pk=sale_summary_id)
    if request.method == 'POST':
        form = SaleSummaryForm(request.POST, instance=sale_summary)
        if form.is_valid():
            form.save()
            return render(request, 'sales_summary/detail.html', {"sale_summary": sale_summary})
    else:
        form = SaleSummaryForm(instance=sale_summary)
    return render(request, 'sales_summary/edit.html', {'form': form})

@login_required
def delete(request, sale_summary_id):
    """
    Render the delete confirmation page for a specific seller.
    """
    sale_summary = get_object_or_404(SaleSummary, pk=sale_summary_id)
    if request.method == 'POST':
        sale_summary.delete()
        return HttpResponse("<h1>Ingreso eliminado exitosamente</h1>")
    
    return render(request, 'sales_summary/delete.html', {'sale_summary': sale_summary})

@login_required
def add_payment(request, sale_id):
    """
    Add a payment to a sale.
    """
    sale = get_object_or_404(Sale, pk=sale_id)
    if request.method == 'POST':
        form = SaleSummaryForm(request.POST)
        if form.is_valid():
            sale_summary = form.save()
            return render(request, 'sales_summary/detail.html', {"sale_summary": sale_summary})
    else:
        form = SaleSummaryForm(initial={'sale': sale})

    return render(request, 'sales_summary/add_payment.html', {'form': form, 'sale': sale})