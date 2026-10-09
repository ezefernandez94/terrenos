from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Faq
from .forms import FaqForm
from projects.models import Project
from django.contrib.auth.decorators import login_required

class FaqCreateView(LoginRequiredMixin, CreateView):
    """
    View to create a new FAQ. ?project=<id> preselects the project.
    """
    model = Faq
    form_class = FaqForm
    template_name = 'faqs/create.html'
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('faqs:index')

    def get_initial(self):
        initial = super().get_initial()
        project_id = self.request.GET.get('project')
        if project_id and project_id.isdigit():
            initial['project'] = project_id
        return initial

    def form_valid(self, form):
        messages.success(self.request, 'Pregunta creada.')
        return super().form_valid(form)

@login_required
def index(request):
    """
    Render the index page of the faqs app: general questions first, then one group per project.
    """
    groups = [{"title": "Generales (página de inicio)", "project": None,
               "faqs": Faq.objects.filter(project__isnull=True)}]
    for project in Project.objects.prefetch_related('faqs').order_by('start_date', 'name'):
        groups.append({"title": project.name, "project": project, "faqs": project.faqs.all()})
    return render(request, 'faqs/index.html', {"groups": groups})

@login_required
def edit(request, faq_id):
    """
    Render the edit page for a specific FAQ.
    """
    faq = get_object_or_404(Faq, pk=faq_id)
    if request.method == 'POST':
        form = FaqForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pregunta actualizada.')
            return redirect('faqs:index')
    else:
        form = FaqForm(instance=faq)
    return render(request, 'faqs/edit.html', {'form': form, 'faq': faq})

@login_required
def delete(request, faq_id):
    """
    Render the delete confirmation page for a specific FAQ.
    """
    faq = get_object_or_404(Faq, pk=faq_id)
    if request.method == 'POST':
        faq.delete()
        messages.success(request, 'Pregunta eliminada.')
        return redirect('faqs:index')

    return render(request, 'faqs/delete.html', {'faq': faq})
