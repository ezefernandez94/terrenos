from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import SaleSummary
from .forms import SaleSummaryForm

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
    
def index(request):
    """
    Render the index page of the sales_summary app.
    """
    sales_summary = SaleSummary.objects.all()
    return render(request, 'sales_summary/index.html', {"sales_summary": sales_summary})

def detail(request, sale_summary_id):
    """
    Render the detail page for a specific sale_summary.
    """
    try:
        sale_summary = SaleSummary.objects.get(id=sale_summary_id)
    except SaleSummary.DoesNotExist:
        raise Http404("<h1>SaleSummary not found</h1>", status=404)
    return render(request, "sales_summary/detail.html", {"sale_summary": sale_summary})

def create(request):
    """
    Render the create sale_summary page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New SaleSummary</h1>")

def edit(request, sale_summary_id):
    """
    Render the edit page for a specific sale_summary.
    """
    # Here you would typically fetch the sale_summary from the database using the sale_summary_id
    # For now, we'll just return a placeholder response
    return HttpResponse(f"<h1>Edit SaleSummary ID: {sale_summary_id}</h1>")

def delete(request, sale_summary_id):
    """
    Render the delete confirmation page for a specific sale_summary.
    """
    # Here you would typically fetch the sale_summary from the database using the sale_summary_id
    # For now, we'll just return a placeholder response
    return HttpResponse(f"<h1>Delete SaleSummary ID: {sale_summary_id}</h1>")

