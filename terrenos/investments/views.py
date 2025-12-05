from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from .models import Investment
from .forms import InvestmentForm
from django.contrib.auth.decorators import login_required

class InvestmentCreateView(CreateView):
    """
    View to create a new investment.
    """
    model = Investment
    form_class = InvestmentForm
    template_name = 'investments/create.html'
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('investments:index')
    
    def form_valid(self, form):
        return super().form_valid(form)
    
class InvestmentDeleteView(DeleteView):
    """
    View to delete a investment.
    """
    model = Investment
    template_name = 'investments/delete.html'
    success_url = reverse_lazy('investments:index')

@login_required
def index(request):
    """
    Render the index page of the investments app.
    """
    ## investments = Investment.objects.all()
    investments = Investment.objects.select_related(
        'expense_type', 
        'expense_type_detail',
        'project',
        'payer',
        'payment_receiver'
    ).all()
    return render(request, 'investments/index.html', {"investments": investments})

@login_required
def detail(request, investment_id):
    """
    Render the detail page for a specific investment.
    """
    try:
        investment = Investment.objects.get(id=investment_id)
    except Investment.DoesNotExist:
        raise Http404("<h1>Investment not found</h1>", status=404)
    return render(request, "investments/detail.html", {"investment": investment})

@login_required
def create(request):
    """
    Render the create investment page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Investment</h1>")

@login_required
def edit(request, investment_id):
    """
    Render the edit page for a specific investment.
    """
    investment = get_object_or_404(Investment, pk=investment_id)
    if request.method == 'POST':
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            form.save()
            return render(request, 'investments/detail.html', {"investment": investment})
    else:
        form = InvestmentForm(instance=investment)
    return render(request, 'investments/edit.html', {'form': form})

@login_required
def delete(request, investment_id):
    """
    Render the delete confirmation page for a specific investment.
    """
    investment = get_object_or_404(Investment, pk=investment_id)
    if request.method == 'POST':
        investment.delete()
        return HttpResponse("<h1>Investment deleted successfully</h1>")
    
    return render(request, 'investments/delete.html', {'investment': investment})

