from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from .models import Project
from .forms import ProjectForm

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
        raise Http404("<h1>Project not found</h1>", status=404)
    return render(request, "projects/detail.html", {"project": project})

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
