from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from .models import ExpenseType
from .forms import ExpenseTypeForm
from django.contrib.auth.decorators import login_required

class ExpenseTypeCreateView(CreateView):
    """
    View to create a new expense_type.
    """
    model = ExpenseType
    form_class = ExpenseTypeForm
    template_name = 'expense_types/create.html'
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('expense_types:index')
    
    def form_valid(self, form):
        return super().form_valid(form)
    
class ExpenseDeleteView(DeleteView):
    """
    View to delete a expense_type.
    """
    model = ExpenseType
    template_name = 'expense_types/delete.html'
    success_url = reverse_lazy('expense_types:index')

@login_required
def index(request):
    """
    Render the index page of the expense_types app.
    """
    expense_types = ExpenseType.objects.all()
    return render(request, 'expense_types/index.html', {"expense_types": expense_types})

@login_required
def detail(request, expense_type_id):
    """
    Render the detail page for a specific expense_type.
    """
    try:
        expense_type = ExpenseType.objects.get(id=expense_type_id)
    except ExpenseType.DoesNotExist:
        raise Http404("<h1>Expense not found</h1>", status=404)
    return render(request, "expense_types/detail.html", {"expense_type": expense_type})

@login_required
def create(request):
    """
    Render the create expense_type page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Expense</h1>")

@login_required
def edit(request, expense_type_id):
    """
    Render the edit page for a specific expense_type.
    """
    expense_type = get_object_or_404(ExpenseType, pk=expense_type_id)
    if request.method == 'POST':
        form = ExpenseTypeForm(request.POST, instance=expense_type)
        if form.is_valid():
            form.save()
            return render(request, 'expense_types/detail.html', {"expense_type": expense_type})
    else:
        form = ExpenseTypeForm(instance=expense_type)
    return render(request, 'expense_types/edit.html', {'form': form})

@login_required
def delete(request, expense_type_id):
    """
    Render the delete confirmation page for a specific expense_type.
    """
    expense_type = get_object_or_404(ExpenseType, pk=expense_type_id)
    if request.method == 'POST':
        expense_type.delete()
        return HttpResponse("<h1>Expense deleted successfully</h1>")
    
    return render(request, 'expense_types/delete.html', {'expense_type': expense_type})

