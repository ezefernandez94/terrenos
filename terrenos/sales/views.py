from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView,DeleteView
from django.urls import reverse_lazy
from .models import Sale
from .forms import SaleForm, PeopleToLandFormSet
from lands.models import Land
from projects.models import Project
from people_to_lands.models import PeopleToLands
from django.contrib.auth.decorators import login_required

class SaleCreateView(LoginRequiredMixin, CreateView):
    """
    View to create a new sale.
    """
    model = Sale
    form_class = SaleForm
    template_name = 'sales/create.html'
    ## Redirect to the index page after successful creation
    success_url = reverse_lazy('sales:index')
    
    def form_valid(self, form):
        return super().form_valid(form)

class SaleDeleteView(LoginRequiredMixin, DeleteView):
    """
    View to delete a sale.
    """
    model = Sale
    template_name = 'sales/delete.html'
    success_url = reverse_lazy('sales:index')

@login_required
def index(request):
    """
    Render the index page of the sales app.
    """
    sales = Sale.objects.select_related('land__project')
    ## Finished projects are hidden unless ?finalizados=1
    show_finished = request.GET.get('finalizados') == '1'
    if not show_finished:
        sales = sales.exclude(land__project__status=Project.FINISHED)
    return render(request, 'sales/index.html', {
        "sales": sales,
        "show_finished": show_finished,
        "finished_count": Project.objects.filter(status=Project.FINISHED).count(),
    })

@login_required
def detail(request, sale_id):
    """
    Render the detail page for a specific sale.
    """
    try:
        sale = Sale.objects.get(id=sale_id)
    except Sale.DoesNotExist:
        raise Http404("<h1>Sale not found</h1>", status=404)
    return render(request, "sales/detail.html", {"sale": sale})

@login_required
def create(request):
    """
    Render the create sale page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Sale</h1>")

@login_required
def edit(request, sale_id):
    """
    Render the edit page for a specific sale.
    """
    sale = get_object_or_404(Sale, pk=sale_id)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            messages.success(request, 'Venta actualizada.')
            return redirect('sales:detail', sale_id=sale.id)
    else:
        form = SaleForm(instance=sale)
    return render(request, 'sales/edit.html', {'form': form, 'sale': sale})

@login_required
def delete(request, sale_id):
    """
    Render the delete confirmation page for a specific sale.
    """
    sale = get_object_or_404(Sale, pk=sale_id)
    if request.method == 'POST':
        sale.delete()
        messages.success(request, 'Venta eliminada.')
        return redirect('sales:index')
    
    return render(request, 'sales/delete.html', {'sale': sale})

@login_required
def sell_land(request, land_id):
    """
    Render the page to sell a specific land.
    """
    land = get_object_or_404(Land, pk=land_id)

    if request.method == 'POST':
        form = SaleForm(request.POST)
        formset = PeopleToLandFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                sale = form.save(commit=False)
                sale.land = land
                sale.save()
                sale.sync_down_payment_summary(form.cleaned_data.get('down_payment_option'))
                ## Rows the user removed or left blank are skipped
                for buyer_form in formset.forms:
                    if not buyer_form.has_changed() or buyer_form in formset.deleted_forms:
                        continue
                    ownership = buyer_form.save(commit=False)
                    ownership.land = land
                    ownership.save()
                land.status = 'sold'
                land.save()
            messages.success(request, f'Se registró la venta de {land}.')
            ## Redirect so reloading the page cannot submit the sale twice
            return redirect('sales:detail', sale_id=sale.id)
    else:
        form = SaleForm(initial={'land': land, 'sale_price': land.price})
        formset = PeopleToLandFormSet(queryset=PeopleToLands.objects.none())

    return render(request, 'sales/sell_land.html', {
        'form': form,
        'formset': formset,
        'land': land
    })