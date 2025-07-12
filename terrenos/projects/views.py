from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Case, When, DecimalField, F, Value

from .models import Project
from .forms import ProjectForm
from investments.models import Investment
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
    ## total_lands = 38
    general_investments = Investment.objects.filter(project_id=project_id)
    property_investments = general_investments.filter(type="property")
    light_materials_investments = general_investments.filter(type="light_project", detail="materials")
    light_labour_investments = general_investments.filter(type="light_project", detail="labour")
    public_light_investments = general_investments.filter(type="public_light")
    gas_investments = general_investments.filter(type="gas_project")
    streets_investments = general_investments.filter(type="streets")
    plans_measurements_investment = general_investments.filter(Q(type="plans") | Q(type="measurement"))
    other_investments = general_investments.filter(type="other")
    
    total_property_investments = property_investments.aggregate(
        total_ars= Sum(
            Case(
                When(currency="ars", then=F("amount")), 
                When(currency="usd", then=F("amount") * F("exchange_rate")),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        ),
        total_usd= Sum(
            Case(
                When(currency="usd", then=F("amount")),
                When(currency="ars", then=F("amount") / F("exchange_rate")),
                default=(Value(0)),
                output_field=DecimalField()
            )
        ),
        total_accountable_ars= Sum(
            Case(
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="ars"), then=F("accountant_amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="usd"), then=F("accountant_amount") * F("exchange_rate")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="ars"), then=F("amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="usd"), then=F("amount") * F("exchange_rate")
                ),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        )
    )

    total_property_investments_ars = total_property_investments["total_ars"] or 0
    total_property_investments_usd = total_property_investments["total_usd"] or 0
    property_ars_per_land = total_property_investments_ars / total_lands
    property_usd_per_land = total_property_investments_usd / total_lands
    

    total_light_materials_investments = light_materials_investments.aggregate(
        total_ars= Sum(
            Case(
                When(currency="ars", then=F("amount")), 
                When(currency="usd", then=F("amount") * F("exchange_rate")),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        ),
        total_usd= Sum(
            Case(
                When(currency="usd", then=F("amount")),
                When(currency="ars", then=F("amount") / F("exchange_rate")),
                default=(Value(0)),
                output_field=DecimalField()
            )
        ),
        total_accountable_ars= Sum(
            Case(
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="ars"), then=F("accountant_amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="usd"), then=F("accountant_amount") * F("exchange_rate")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="ars"), then=F("amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="usd"), then=F("amount") * F("exchange_rate")
                ),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        )
    )

    total_light_materials_investments_ars = total_light_materials_investments["total_ars"] or 0
    total_light_materials_investments_usd = total_light_materials_investments["total_usd"] or 0
    light_materials_ars_per_land = total_light_materials_investments_ars / total_lands
    light_materials_usd_per_land = total_light_materials_investments_usd / total_lands

    total_light_labour_investments = light_labour_investments.aggregate(
        total_ars= Sum(
            Case(
                When(currency="ars", then=F("amount")), 
                When(currency="usd", then=F("amount") * F("exchange_rate")),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        ),
        total_usd= Sum(
            Case(
                When(currency="usd", then=F("amount")),
                When(currency="ars", then=F("amount") / F("exchange_rate")),
                default=(Value(0)),
                output_field=DecimalField()
            )
        ),
        total_accountable_ars= Sum(
            Case(
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="ars"), then=F("accountant_amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="usd"), then=F("accountant_amount") * F("exchange_rate")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="ars"), then=F("amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="usd"), then=F("amount") * F("exchange_rate")
                ),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        )
    )

    total_light_labour_investments_ars = total_light_labour_investments["total_ars"] or 0
    total_light_labour_investments_usd = total_light_labour_investments["total_usd"] or 0
    light_labour_ars_per_land = total_light_labour_investments_ars / total_lands
    light_labour_usd_per_land = total_light_labour_investments_usd / total_lands

    total_public_light_investments = public_light_investments.aggregate(
        total_ars= Sum(
            Case(
                When(currency="ars", then=F("amount")), 
                When(currency="usd", then=F("amount") * F("exchange_rate")),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        ),
        total_usd= Sum(
            Case(
                When(currency="usd", then=F("amount")),
                When(currency="ars", then=F("amount") / F("exchange_rate")),
                default=(Value(0)),
                output_field=DecimalField()
            )
        ),
        total_accountable_ars= Sum(
            Case(
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="ars"), then=F("accountant_amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="usd"), then=F("accountant_amount") * F("exchange_rate")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="ars"), then=F("amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="usd"), then=F("amount") * F("exchange_rate")
                ),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        )
    )

    total_public_light_investments_ars = total_public_light_investments["total_ars"] or 0
    total_public_light_investments_usd = total_public_light_investments["total_usd"] or 0
    public_light_ars_per_land = total_public_light_investments_ars / total_lands
    public_light_usd_per_land = total_public_light_investments_usd / total_lands

    total_gas_investments = gas_investments.aggregate(
        total_ars= Sum(
            Case(
                When(currency="ars", then=F("amount")), 
                When(currency="usd", then=F("amount") * F("exchange_rate")),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        ),
        total_usd= Sum(
            Case(
                When(currency="usd", then=F("amount")),
                When(currency="ars", then=F("amount") / F("exchange_rate")),
                default=(Value(0)),
                output_field=DecimalField()
            )
        ),
        total_accountable_ars= Sum(
            Case(
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="ars"), then=F("accountant_amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="usd"), then=F("accountant_amount") * F("exchange_rate")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="ars"), then=F("amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="usd"), then=F("amount") * F("exchange_rate")
                ),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        )
    )

    total_gas_investments_ars = total_gas_investments["total_ars"] or 0
    total_gas_investments_usd = total_gas_investments["total_usd"] or 0
    gas_ars_per_land = total_gas_investments_ars / total_lands
    gas_usd_per_land = total_gas_investments_usd / total_lands

    total_streets_investments = streets_investments.aggregate(
        total_ars= Sum(
            Case(
                When(currency="ars", then=F("amount")), 
                When(currency="usd", then=F("amount") * F("exchange_rate")),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        ),
        total_usd= Sum(
            Case(
                When(currency="usd", then=F("amount")),
                When(currency="ars", then=F("amount") / F("exchange_rate")),
                default=(Value(0)),
                output_field=DecimalField()
            )
        ),
        total_accountable_ars= Sum(
            Case(
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="ars"), then=F("accountant_amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="usd"), then=F("accountant_amount") * F("exchange_rate")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="ars"), then=F("amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="usd"), then=F("amount") * F("exchange_rate")
                ),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        )
    )

    total_streets_investments_ars = total_streets_investments["total_ars"] or 0
    total_streets_investments_usd = total_streets_investments["total_usd"] or 0
    street_ars_per_land = total_streets_investments_ars / total_lands
    street_usd_per_land = total_streets_investments_usd / total_lands

    total_plans_measurements_investment = plans_measurements_investment.aggregate(
        total_ars= Sum(
            Case(
                When(currency="ars", then=F("amount")), 
                When(currency="usd", then=F("amount") * F("exchange_rate")),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        ),
        total_usd= Sum(
            Case(
                When(currency="usd", then=F("amount")),
                When(currency="ars", then=F("amount") / F("exchange_rate")),
                default=(Value(0)),
                output_field=DecimalField()
            )
        ),
        total_accountable_ars= Sum(
            Case(
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="ars"), then=F("accountant_amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="usd"), then=F("accountant_amount") * F("exchange_rate")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="ars"), then=F("amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="usd"), then=F("amount") * F("exchange_rate")
                ),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        )
    )

    total_plans_measurements_investment_ars = total_plans_measurements_investment["total_ars"] or 0
    total_plans_measurements_investment_usd = total_plans_measurements_investment["total_usd"] or 0
    plans_measurement_ars_per_land = total_plans_measurements_investment_ars / total_lands
    plans_measurement_usd_per_land = total_plans_measurements_investment_usd / total_lands

    total_other_investments = other_investments.aggregate(
        total_ars= Sum(
            Case(
                When(currency="ars", then=F("amount")), 
                When(currency="usd", then=F("amount") * F("exchange_rate")),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        ),
        total_usd= Sum(
            Case(
                When(currency="usd", then=F("amount")),
                When(currency="ars", then=F("amount") / F("exchange_rate")),
                default=(Value(0)),
                output_field=DecimalField()
            )
        ),
        total_accountable_ars= Sum(
            Case(
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="ars"), then=F("accountant_amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=False) & Q(accountant_currency="usd"), then=F("accountant_amount") * F("exchange_rate")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="ars"), then=F("amount")
                ),
                When(
                    Q(accountant=True) & Q(accountant_amount__isnull=True) & Q(currency="usd"), then=F("amount") * F("exchange_rate")
                ),
                default=(Value(0)), 
                output_field=DecimalField()
            )
        )
    )

    total_other_investments_ars = total_other_investments["total_ars"] or 0
    total_other_investments_usd = total_other_investments["total_usd"] or 0
    other_ars_per_land = total_other_investments_ars / total_lands
    other_usd_per_land = total_other_investments_usd / total_lands

    
    return render(request, "projects/detail.html", {
        "project": project,
        "total_lands": total_lands,
        "property_investments": property_investments,
        "light_materials_investments": light_materials_investments,
        "light_labour_investments": light_labour_investments,
        "public_light_investments": public_light_investments,
        "gas_investments": gas_investments,
        "streets_investments": streets_investments,
        "plans_measurements_investment": plans_measurements_investment,
        "other_investment": other_investments,
        "total_property_investments": total_property_investments,
        "property_ars_per_land": property_ars_per_land,
        "property_usd_per_land": property_usd_per_land,
        "total_light_materials_investments": total_light_materials_investments,
        "light_materials_ars_per_land": light_materials_ars_per_land,
        "light_materials_usd_per_land": light_materials_usd_per_land,
        "total_light_labour_investments": total_light_labour_investments,
        "light_labour_ars_per_land": light_labour_ars_per_land,
        "light_labour_usd_per_land": light_labour_usd_per_land,
        "total_public_light_investments": total_public_light_investments,
        "public_light_ars_per_land": public_light_ars_per_land,
        "public_light_usd_per_land": public_light_usd_per_land,
        "total_gas_investments": total_gas_investments,
        "gas_ars_per_land": gas_ars_per_land,
        "gas_usd_per_land": gas_usd_per_land,
        "total_street_investments": total_streets_investments,
        "street_ars_per_land": street_ars_per_land,
        "street_usd_per_land": street_usd_per_land,
        "total_plans_measurements_investments": total_plans_measurements_investment,
        "plans_measurement_ars_per_land": plans_measurement_ars_per_land,
        "plans_measurement_usd_per_land": plans_measurement_usd_per_land,
        "total_other_investments": total_other_investments,
        "other_ars_per_land": other_ars_per_land,
        "other_usd_per_land": other_usd_per_land,
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
