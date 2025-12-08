from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Case, When, DecimalField, F, Value, Avg

from .models import Project
from .forms import ProjectForm
from investments.models import Investment
from expense_types.models import ExpenseType
from expense_type_details.models import ExpenseTypeDetail
from django.contrib.auth.decorators import login_required

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

@login_required
def index(request):
    """
    Render the index page of the projects app.
    """
    projects = Project.objects.all()
    ## return render(request, 'projects/index.html')
    return render(request, 'projects/index.html', {"projects": projects})

@login_required
def detail(request, project_id):
    """
    Render the detail page for a specific project.
    """
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("<h1>El proyecto que está solicitando no existe</h1>", status=404)
    
    total_lands = project.land_set.count()
    
    if total_lands > 0:
        # Obtener todos los expense types
        expense_types = ExpenseType.objects.all().order_by('id')
        
        # Diccionario para almacenar los datos de cada expense_type
        expense_type_data = {}
        
        # Variables para totales generales
        total_general_ars = 0
        total_general_usd = 0
        total_general_accountable_ars = 0
        
        for expense_type in expense_types:
            # Filtrar inversiones por este expense_type
            investments = Investment.objects.filter(
                project_id=project_id,
                expense_type_id=expense_type.id
            ).select_related('expense_type_detail', 'payer', 'payment_receiver')
            
            # Calcular totales
            totals = investments.aggregate(
                total_ars=Sum(
                    Case(
                        When(currency="ars", then=F("amount")), 
                        When(currency="usd", then=F("amount") * F("exchange_rate")),
                        default=Value(0), 
                        output_field=DecimalField()
                    )
                ),
                total_usd=Sum(
                    Case(
                        When(currency="usd", then=F("amount")),
                        When(currency="ars", then=F("amount") / F("exchange_rate")),
                        default=Value(0),
                        output_field=DecimalField()
                    )
                ),
                total_accountable_ars=Sum(
                    Case(
                        When(
                            Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="ars"), 
                            then=F("accountant_amount")
                        ),
                        When(
                            Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="usd"), 
                            then=F("accountant_amount") * F("exchange_rate")
                        ),
                        When(
                            Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="ars"), 
                            then=F("amount")
                        ),
                        When(
                            Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="usd"), 
                            then=F("amount") * F("exchange_rate")
                        ),
                        default=Value(0), 
                        output_field=DecimalField()
                    )
                ),
                avg_exchange_rate=Avg('exchange_rate')
            )
            
            # Extraer valores y manejar None
            total_ars = totals["total_ars"] or 0
            total_usd = totals["total_usd"] or 0
            total_accountable_ars = totals["total_accountable_ars"] or 0
            avg_exchange_rate = totals["avg_exchange_rate"] or 0
            
            # Acumular totales generales
            total_general_ars += total_ars
            total_general_usd += total_usd
            total_general_accountable_ars += total_accountable_ars
            
            # Calcular por lote
            ars_per_land = total_ars / total_lands
            usd_per_land = total_usd / total_lands
            
            # Guardar en el diccionario
            expense_type_data[expense_type.key] = {
                'expense_type': expense_type,
                'investments': investments,
                'total_ars': total_ars,
                'total_usd': total_usd,
                'total_accountable_ars': total_accountable_ars,
                'ars_per_land': ars_per_land,
                'usd_per_land': usd_per_land,
                'avg_exchange_rate': avg_exchange_rate,
                'percentage_of_total': 0,
            }

        if total_general_ars > 0:
            for key in expense_type_data:
                expense_type_data[key]['percentage_of_total'] = (
                    expense_type_data[key]['total_ars'] / total_general_ars * 100
                )
        
        # Calcular totales generales por lote
        total_general_ars_per_land = total_general_ars / total_lands
        total_general_usd_per_land = total_general_usd / total_lands
        
        return render(request, "projects/detail.html", {
            "project": project,
            "total_lands": total_lands,
            "expense_type_data": expense_type_data,
            "total_general_ars": total_general_ars,
            "total_general_usd": total_general_usd,
            "total_general_accountable_ars": total_general_accountable_ars,
            "total_general_ars_per_land": total_general_ars_per_land,
            "total_general_usd_per_land": total_general_usd_per_land,
        })
    else:
        return render(request, "projects/detail.html", {
            "project": project,
            "total_lands": total_lands
        })
    
@login_required
def create(request):
    """
    Render the create project page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Project</h1>")

@login_required
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

@login_required
def delete(request, project_id):
    """
    Render the delete confirmation page for a specific project.
    """
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        project.delete()
        return HttpResponse("<h1>Project deleted successfully</h1>")
    
    return render(request, 'projects/delete.html', {'project': project})
