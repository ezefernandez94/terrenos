from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import People
from .forms import PeopleForm

class PeopleCreateView(CreateView):
    """
    View to create a new people.
    """
    model = People
    form_class = PeopleForm
    template_name = 'peoples/create.html'
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('peoples:index')
    
    def form_valid(self, form):
        return super().form_valid(form)
    
def index(request):
    """
    Render the index page of the peoples app.
    """
    peoples = People.objects.all()
    return render(request, 'peoples/index.html', {"peoples": peoples})

def detail(request, people_id):
    """
    Render the detail page for a specific people.
    """
    try:
        people = People.objects.get(id=people_id)
    except People.DoesNotExist:
        raise Http404("<h1>People not found</h1>", status=404)
    return render(request, "peoples/detail.html", {"people": people})

def create(request):
    """
    Render the create people page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New People</h1>")

def edit(request, people_id):
    """
    Render the edit page for a specific people.
    """
    # Here you would typically fetch the people from the database using the people_id
    # For now, we'll just return a placeholder response
    return HttpResponse(f"<h1>Edit People ID: {people_id}</h1>")

def delete(request, people_id):
    """
    Render the delete confirmation page for a specific people.
    """
    # Here you would typically fetch the people from the database using the people_id
    # For now, we'll just return a placeholder response
    return HttpResponse(f"<h1>Delete People ID: {people_id}</h1>")

