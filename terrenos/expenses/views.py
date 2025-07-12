from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from .models import Expense
from .forms import ExpenseForm
import os
from django.contrib.auth.decorators import login_required

class ExpenseCreateView(CreateView):
    """
    View to create a new expense.
    """
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/create.html'
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('expenses:index')
    
    def form_valid(self, form):
        return super().form_valid(form)
    
class ExpenseDeleteView(DeleteView):
    """
    View to delete a expense.
    """
    model = Expense
    template_name = 'expenses/delete.html'
    success_url = reverse_lazy('expenses:index')

@login_required
def index(request):
    """
    Render the index page of the expenses app.
    """
    expenses = Expense.objects.all()
    return render(request, 'expenses/index.html', {"expenses": expenses})

@login_required
def detail(request, expense_id):
    """
    Render the detail page for a specific expense.
    """
    try:
        expense = Expense.objects.get(id=expense_id)
    except Expense.DoesNotExist:
        raise Http404("<h1>Expense not found</h1>", status=404)
    return render(request, "expenses/detail.html", {"expense": expense})

@login_required
def serve_file(request, expense_id):
    record = get_object_or_404(Expense, pk=expense_id)
    
    if not record.receipt:
        raise Http404("File not found")
    
    file_path = record.receipt.path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    raise Http404("File not found")

@login_required
def create(request):
    """
    Render the create expense page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Expense</h1>")

@login_required
def edit(request, expense_id):
    """
    Render the edit page for a specific expense.
    """
    expense = get_object_or_404(Expense, pk=expense_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return render(request, 'expenses/detail.html', {"expense": expense})
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/edit.html', {'form': form})

@login_required
def delete(request, expense_id):
    """
    Render the delete confirmation page for a specific expense.
    """
    expense = get_object_or_404(Expense, pk=expense_id)
    if request.method == 'POST':
        expense.delete()
        return HttpResponse("<h1>Expense deleted successfully</h1>")
    
    return render(request, 'expenses/delete.html', {'expense': expense})

