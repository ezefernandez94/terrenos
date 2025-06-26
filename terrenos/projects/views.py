from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q

from .models import Project
from .forms import ProjectForm
from expenses.models import Expense

class ProjectCreateView(CreateView):
    """
    View to create a new project.
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create.html'
    ## fields = ['name', 'start_date', 'end_date']
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('projects:index')
    
    def form_valid(self, form):
        return super().form_valid(form)
    
class ProjectDeleteView(DeleteView):
    """
    View to delete a project.
    """
    model = Project
    template_name = 'projects/delete.html'
    success_url = reverse_lazy('projects:index')

def index(request):
    """
    Render the index page of the projects app.
    """
    projects = Project.objects.all()
    ## return render(request, 'projects/index.html')
    return render(request, 'projects/index.html', {"projects": projects})

def detail(request, project_id):
    """
    Render the detail page for a specific project.
    """
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("<h1>El proyecto que está solicitando no existe</h1>", status=404)
    
    general_expenses = Expense.objects.filter(project_id=project_id)
    property_expenses = general_expenses.filter(type="property")
    light_materials_expenses = general_expenses.filter(type="light_project", detail="materials")
    light_labour_expenses = general_expenses.filter(type="light_project", detail="labour")
    gas_expenses = general_expenses.filter(type="gas_project")
    streets_expenses = general_expenses.filter(type="streets")
    plans_measurements_expense = general_expenses.filter(Q(type="plans") | Q(type="measurement"))
    other_expenses = general_expenses.filter(type="other")

    return render(request, "projects/detail.html", {
        "project": project,
        "property_expenses": property_expenses,
        "light_materials_expenses": light_materials_expenses,
        "light_labour_expenses": light_labour_expenses,
        "gas_expenses": gas_expenses,
        "streets_expenses": streets_expenses,
        "plans_measurements_expense": plans_measurements_expense,
        "other_expenses": other_expenses
    })

def create(request):
    """
    Render the create project page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Project</h1>")

def edit(request, project_id):
    """
    Render the edit page for a specific project.
    """
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return render(request, 'projects/detail.html', {"project": project})
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/edit.html', {'form': form})


def delete(request, project_id):
    """
    Render the delete confirmation page for a specific project.
    """
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        project.delete()
        return HttpResponse("<h1>Project deleted successfully</h1>")
    
    return render(request, 'projects/delete.html', {'project': project})
