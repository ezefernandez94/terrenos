from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.forms import modelformset_factory
from .models import Land
from .forms import LandForm
from projects.models import Project

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
    
class LandDeleteView(DeleteView):
    """
    View to delete a land.
    """
    model = Land
    template_name = 'lands/delete.html'
    success_url = reverse_lazy('lands:index')

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

def create_multiple(request, project_id):
    """
    Render the page to create multiple lands.
    """
    project = get_object_or_404(Project, pk=project_id)
    LandFormSet = modelformset_factory(Land, form=LandForm, extra=0, can_delete=False)

    if request.method == 'POST':
        formset = LandFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                instance = form.save(commit=False)
                instance.project = project
                instance.save()
            return render(request, 'lands/index.html', {'lands': Land.objects.all()})
        else:
            print(formset.errors)
    else:
        formset = LandFormSet(queryset=Land.objects.none())

    return render(request, 'lands/create_multiple.html', {'formset': formset, 'project': project})

def edit(request, land_id):
    """
    Render the edit page for a specific land.
    """
    land = get_object_or_404(Land, pk=land_id)
    if request.method == 'POST':
        form = LandForm(request.POST, instance=land)
        if form.is_valid():
            form.save()
            return render(request, 'lands/detail.html', {"land": land})
    else:
        form = LandForm(instance=land)
    return render(request, 'lands/edit.html', {'form': form})


def delete(request, land_id):
    """
    Render the delete confirmation page for a specific land.
    """
    land = get_object_or_404(Land, pk=land_id)
    if request.method == 'POST':
        land.delete()
        return redirect(reverse("lands:index"))
    
    return render(request, 'lands/delete.html', {'land': land})

def sell(request, land_id):
    """
    Render the sell page for a specific land.
    """
    land = get_object_or_404(Land, pk=land_id)
    if request.method == 'POST':
        land.status = 'sold'
        land.save()
        return render(request, 'lands/detail.html', {"land": land})
    
    return render(request, 'sales/create.html', {'land': land})