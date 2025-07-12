from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from .models import ExpenseTypeDetail
from .forms import ExpenseTypeDetailForm
from django.contrib.auth.decorators import login_required

class ExpenseTypeDetailCreateView(CreateView):
    """
    View to create a new expense_type_detail.
    """
    model = ExpenseTypeDetail
    form_class = ExpenseTypeDetailForm
    template_name = 'expense_type_details/create.html'
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('expense_type_details:index')
    
    def form_valid(self, form):
        return super().form_valid(form)
    
class ExpenseDeleteView(DeleteView):
    """
    View to delete a expense_type_detail.
    """
    model = ExpenseTypeDetail
    template_name = 'expense_type_details/delete.html'
    success_url = reverse_lazy('expense_type_details:index')

@login_required
def index(request):
    """
    Render the index page of the expense_type_details app.
    """
    expense_type_details = ExpenseTypeDetail.objects.all()
    return render(request, 'expense_type_details/index.html', {"expense_type_details": expense_type_details})

@login_required
def detail(request, expense_type_detail_id):
    """
    Render the detail page for a specific expense_type_detail.
    """
    try:
        expense_type_detail = ExpenseTypeDetail.objects.get(id=expense_type_detail_id)
    except ExpenseTypeDetail.DoesNotExist:
        raise Http404("<h1>Expense not found</h1>", status=404)
    return render(request, "expense_type_details/detail.html", {"expense_type_detail": expense_type_detail})

@login_required
def create(request):
    """
    Render the create expense_type_detail page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Expense</h1>")

@login_required
def edit(request, expense_type_detail_id):
    """
    Render the edit page for a specific expense_type_detail.
    """
    expense_type_detail = get_object_or_404(ExpenseTypeDetail, pk=expense_type_detail_id)
    if request.method == 'POST':
        form = ExpenseTypeDetailForm(request.POST, instance=expense_type_detail)
        if form.is_valid():
            form.save()
            return render(request, 'expense_type_details/detail.html', {"expense_type_detail": expense_type_detail})
    else:
        form = ExpenseTypeDetailForm(instance=expense_type_detail)
    return render(request, 'expense_type_details/edit.html', {'form': form})

@login_required
def delete(request, expense_type_detail_id):
    """
    Render the delete confirmation page for a specific expense_type_detail.
    """
    expense_type_detail = get_object_or_404(ExpenseTypeDetail, pk=expense_type_detail_id)
    if request.method == 'POST':
        expense_type_detail.delete()
        return HttpResponse("<h1>Expense deleted successfully</h1>")
    
    return render(request, 'expense_type_details/delete.html', {'expense_type_detail': expense_type_detail})

