from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Land
from .forms import LandForm

class LandCreateView(CreateView):
    """
    View to create a new land.
    """
    model = Land
    form_class = LandForm
    template_name = 'lands/create.html'
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('lands:index')
    
    def form_valid(self, form):
        return super().form_valid(form)
    
def index(request):
    """
    Render the index page of the lands app.
    """
    lands = Land.objects.all()
    return render(request, 'lands/index.html', {"lands": lands})

def detail(request, land_id):
    """
    Render the detail page for a specific land.
    """
    try:
        land = Land.objects.get(id=land_id)
    except Land.DoesNotExist:
        raise Http404("<h1>Land not found</h1>", status=404)
    return render(request, "lands/detail.html", {"land": land})

def create(request):
    """
    Render the create land page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Land</h1>")

def edit(request, land_id):
    """
    Render the edit page for a specific land.
    """
    # Here you would typically fetch the land from the database using the land_id
    # For now, we'll just return a placeholder response
    return HttpResponse(f"<h1>Edit Land ID: {land_id}</h1>")

def delete(request, land_id):
    """
    Render the delete confirmation page for a specific land.
    """
    # Here you would typically fetch the land from the database using the land_id
    # For now, we'll just return a placeholder response
    return HttpResponse(f"<h1>Delete Land ID: {land_id}</h1>")

