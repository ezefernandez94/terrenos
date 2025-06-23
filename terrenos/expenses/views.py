from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Expense
from .forms import ExpenseForm

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
    
def index(request):
    """
    Render the index page of the expenses app.
    """
    expenses = Expense.objects.all()
    return render(request, 'expenses/index.html', {"expenses": expenses})

def detail(request, expense_id):
    """
    Render the detail page for a specific expense.
    """
    try:
        expense = Expense.objects.get(id=expense_id)
    except Expense.DoesNotExist:
        raise Http404("<h1>Expense not found</h1>", status=404)
    return render(request, "expenses/detail.html", {"expense": expense})

def create(request):
    """
    Render the create expense page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Expense</h1>")

def edit(request, expense_id):
    """
    Render the edit page for a specific expense.
    """
    # Here you would typically fetch the expense from the database using the expense_id
    # For now, we'll just return a placeholder response
    return HttpResponse(f"<h1>Edit Expense ID: {expense_id}</h1>")

def delete(request, expense_id):
    """
    Render the delete confirmation page for a specific expense.
    """
    # Here you would typically fetch the expense from the database using the expense_id
    # For now, we'll just return a placeholder response
    return HttpResponse(f"<h1>Delete Expense ID: {expense_id}</h1>")

