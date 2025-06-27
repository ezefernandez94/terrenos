from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Case, When, DecimalField, F, Value

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
    
    total_lands = project.land_set.count()
    general_expenses = Expense.objects.filter(project_id=project_id)
    property_expenses = general_expenses.filter(type="property")
    light_materials_expenses = general_expenses.filter(type="light_project", detail="materials")
    light_labour_expenses = general_expenses.filter(type="light_project", detail="labour")
    public_light_expenses = general_expenses.filter(type="public_light")
    gas_expenses = general_expenses.filter(type="gas_project")
    streets_expenses = general_expenses.filter(type="streets")
    plans_measurements_expense = general_expenses.filter(Q(type="plans") | Q(type="measurement"))
    other_expenses = general_expenses.filter(type="other")
    
    total_property_expenses = property_expenses.aggregate(
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

    total_property_expenses_ars = total_property_expenses["total_ars"] or 0
    total_property_expenses_usd = total_property_expenses["total_usd"] or 0
    property_ars_per_land = total_property_expenses_ars / total_lands
    property_usd_per_land = total_property_expenses_usd / total_lands
    

    total_light_materials_expenses = light_materials_expenses.aggregate(
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

    total_light_materials_expenses_ars = total_light_materials_expenses["total_ars"] or 0
    total_light_materials_expenses_usd = total_light_materials_expenses["total_usd"] or 0
    light_materials_ars_per_land = total_light_materials_expenses_ars / total_lands
    light_materials_usd_per_land = total_light_materials_expenses_usd / total_lands

    total_light_labour_expenses = light_labour_expenses.aggregate(
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

    total_light_labour_expenses_ars = total_light_labour_expenses["total_ars"] or 0
    total_light_labour_expenses_usd = total_light_labour_expenses["total_usd"] or 0
    light_labour_ars_per_land = total_light_labour_expenses_ars / total_lands
    light_labour_usd_per_land = total_light_labour_expenses_usd / total_lands

    total_public_light_expenses = public_light_expenses.aggregate(
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

    total_public_light_expenses_ars = total_public_light_expenses["total_ars"] or 0
    total_public_light_expenses_usd = total_public_light_expenses["total_usd"] or 0
    public_light_ars_per_land = total_public_light_expenses_ars / total_lands
    public_light_usd_per_land = total_public_light_expenses_usd / total_lands

    total_gas_expenses = gas_expenses.aggregate(
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

    total_gas_expenses_ars = total_gas_expenses["total_ars"] or 0
    total_gas_expenses_usd = total_gas_expenses["total_usd"] or 0
    gas_ars_per_land = total_gas_expenses_ars / total_lands
    gas_usd_per_land = total_gas_expenses_usd / total_lands

    total_streets_expenses = streets_expenses.aggregate(
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

    total_streets_expenses_ars = total_streets_expenses["total_ars"] or 0
    total_streets_expenses_usd = total_streets_expenses["total_usd"] or 0
    street_ars_per_land = total_streets_expenses_ars / total_lands
    street_usd_per_land = total_streets_expenses_usd / total_lands

    total_plans_measurements_expense = plans_measurements_expense.aggregate(
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

    total_plans_measurements_expense_ars = total_plans_measurements_expense["total_ars"] or 0
    total_plans_measurements_expense_usd = total_plans_measurements_expense["total_usd"] or 0
    plans_measurement_ars_per_land = total_plans_measurements_expense_ars / total_lands
    plans_measurement_usd_per_land = total_plans_measurements_expense_usd / total_lands

    total_other_expenses = other_expenses.aggregate(
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

    total_other_expenses_ars = total_other_expenses["total_ars"] or 0
    total_other_expenses_usd = total_other_expenses["total_usd"] or 0
    other_ars_per_land = total_other_expenses_ars / total_lands
    other_usd_per_land = total_other_expenses_usd / total_lands

    
    return render(request, "projects/detail.html", {
        "project": project,
        "total_lands": total_lands,
        "property_expenses": property_expenses,
        "light_materials_expenses": light_materials_expenses,
        "light_labour_expenses": light_labour_expenses,
        "public_light_expenses": public_light_expenses,
        "gas_expenses": gas_expenses,
        "streets_expenses": streets_expenses,
        "plans_measurements_expense": plans_measurements_expense,
        "other_expense": other_expenses,
        "total_property_expenses": total_property_expenses,
        "property_ars_per_land": property_ars_per_land,
        "property_usd_per_land": property_usd_per_land,
        "total_light_materials_expenses": total_light_materials_expenses,
        "light_materials_ars_per_land": light_materials_ars_per_land,
        "light_materials_usd_per_land": light_materials_usd_per_land,
        "total_light_labour_expenses": total_light_labour_expenses,
        "light_labour_ars_per_land": light_labour_ars_per_land,
        "light_labour_usd_per_land": light_labour_usd_per_land,
        "total_public_light_expenses": total_public_light_expenses,
        "public_light_ars_per_land": public_light_ars_per_land,
        "public_light_usd_per_land": public_light_usd_per_land,
        "total_gas_expenses": total_gas_expenses,
        "gas_ars_per_land": gas_ars_per_land,
        "gas_usd_per_land": gas_usd_per_land,
        "total_street_expenses": total_streets_expenses,
        "street_ars_per_land": street_ars_per_land,
        "street_usd_per_land": street_usd_per_land,
        "total_plans_measurements_expenses": total_plans_measurements_expense,
        "plans_measurement_ars_per_land": plans_measurement_ars_per_land,
        "plans_measurement_usd_per_land": plans_measurement_usd_per_land,
        "total_other_expenses": total_other_expenses,
        "other_ars_per_land": other_ars_per_land,
        "other_usd_per_land": other_usd_per_land,
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
