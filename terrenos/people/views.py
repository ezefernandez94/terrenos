from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from .models import People
from .forms import PeopleForm

class PeopleCreateView(CreateView):
    """
    View to create a new people.
    """
    model = People
    form_class = PeopleForm
    template_name = 'people/create.html'
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('people:index')
    
    def form_valid(self, form):
        return super().form_valid(form)
    
class PeopleDeleteView(DeleteView):
    """
    View to delete a people.
    """
    model = People
    template_name = 'people/delete.html'
    success_url = reverse_lazy('people:index')

def index(request):
    """
    Render the index page of the people app.
    """
    people = People.objects.all()
    return render(request, 'people/index.html', {"people": people})

def detail(request, people_id):
    """
    Render the detail page for a specific people.
    """
    try:
        people = People.objects.get(id=people_id)
    except People.DoesNotExist:
        raise Http404("<h1>People not found</h1>", status=404)
    return render(request, "people/detail.html", {"people": people})

def create(request):
    """
    Render the create people page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New People</h1>")

def edit(request, people_id):
    """
    Render the edit page for a specific person.
    """
    people = get_object_or_404(People, pk=people_id)
    if request.method == 'POST':
        form = PeopleForm(request.POST, instance=people)
        if form.is_valid():
            form.save()
            return render(request, 'people/detail.html', {"people": people})
    else:
        form = PeopleForm(instance=people)
    return render(request, 'people/edit.html', {'form': form})


def delete(request, people_id):
    """
    Render the delete confirmation page for a specific person.
    """
    people = get_object_or_404(People, pk=people_id)
    if request.method == 'POST':
        people.delete()
        return HttpResponse("<h1>People deleted successfully</h1>")
    
    return render(request, 'people/delete.html', {'people': people})
