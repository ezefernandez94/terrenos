from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.views.generic import CreateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal, InvalidOperation
from .models import Land
from .forms import LandForm
from projects.models import Project
from django.contrib.auth.decorators import login_required

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

@login_required
def index(request):
    """
    Render the index page of the lands app.
    """
    lands = Land.objects.all()
    return render(request, 'lands/index.html', {"lands": lands})

@login_required
def detail(request, land_id):
    """
    Render the detail page for a specific land.
    """
    try:
        land = Land.objects.get(id=land_id)
    except Land.DoesNotExist:
        raise Http404("<h1>Land not found</h1>", status=404)
    return render(request, "lands/detail.html", {"land": land})

@login_required
def create(request):
    """
    Render the create land page.
    """
    # In a real application, you would handle form submission here
    return HttpResponse("<h1>Create a New Land</h1>")

@login_required
def create_multiple(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        
        # Validate project
        if str(project.id) != str(project_id):
            messages.error(request, 'Error: El proyecto no coincide.')
            return redirect('lands:create_multiple', project_id=project.id)

        # Parse lands data from POST
        lands_data = []
        index = 0
        
        while f'lands[{index}][manual_id]' in request.POST:
            try:
                # Extract data for this land
                manual_id = request.POST.get(f'lands[{index}][manual_id]', '').strip()
                block = request.POST.get(f'lands[{index}][block]', '').strip()
                length = request.POST.get(f'lands[{index}][length]', '').strip()
                width = request.POST.get(f'lands[{index}][width]', '').strip()
                price = request.POST.get(f'lands[{index}][price]', '').strip()
                currency = request.POST.get(f'lands[{index}][currency]', '').strip()
                type_value = request.POST.get(f'lands[{index}][type]', '').strip()
                status = request.POST.get(f'lands[{index}][status]', '').strip()
                notes = request.POST.get(f'lands[{index}][notes]', '').strip()

                # Validate required fields
                if not all([manual_id, block, length, width, currency, type_value, status]):
                    messages.error(request, f'Error en terreno {index + 1}: Faltan campos obligatorios.')
                    return render(request, 'lands/create_multiple.html', {'project': project})

                # Convert numeric fields
                try:
                    length_decimal = Decimal(length)
                    width_decimal = Decimal(width)
                    price_decimal = Decimal(price) if price else None
                except (InvalidOperation, ValueError):
                    messages.error(request, f'Error en terreno {index + 1}: Valores numéricos inválidos.')
                    return render(request, 'lands/create_multiple.html', {'project': project})

                lands_data.append({
                    'manual_id': manual_id,
                    'block': block,
                    'length': length_decimal,
                    'width': width_decimal,
                    'price': price_decimal,
                    'currency': currency,
                    'type': type_value,
                    'status': status,
                    'notes': notes if notes else None,
                })

            except Exception as e:
                messages.error(request, f'Error procesando terreno {index + 1}: {str(e)}')
                return render(request, 'lands/create_multiple.html', {'project': project})
            
            index += 1

        # Validate that we have at least one land
        if not lands_data:
            messages.error(request, 'Debe proporcionar al menos un terreno.')
            return render(request, 'lands/create_multiple.html', {'project': project})

        # Check for duplicate combinations within the submitted data
        seen_combinations = set()
        for i, land_data in enumerate(lands_data):
            combination = (
                land_data['manual_id'],
                land_data['block'],
                str(land_data['length']),
                str(land_data['width'])
            )
            if combination in seen_combinations:
                messages.error(
                    request,
                    f'Error: Combinación duplicada en terreno {i + 1} '
                    f'(Manual ID: {land_data["manual_id"]}, '
                    f'Manzana: {land_data["block"]}, '
                    f'Largo: {land_data["length"]}, '
                    f'Ancho: {land_data["width"]})'
                )
                return render(request, 'lands/create_multiple.html', {'project': project})
            seen_combinations.add(combination)

        # Check for existing duplicates in database
        # Build a query to check if any of these combinations already exist for this project
        query = Q()
        for land_data in lands_data:
            query |= Q(
                manual_id=land_data['manual_id'],
                block=land_data['block'],
                length=land_data['length'],
                width=land_data['width'],
                project=project
            )
        
        existing_lands = Land.objects.filter(query)
        if existing_lands.exists():
            # Get details of first duplicate for error message
            first_dup = existing_lands.first()
            messages.error(
                request,
                f'Error: Ya existe un terreno con la combinación '
                f'(Manual ID: {first_dup.manual_id}, '
                f'Manzana: {first_dup.block}, '
                f'Largo: {first_dup.length}, '
                f'Ancho: {first_dup.width}) en este proyecto.'
            )
            return render(request, 'lands/create_multiple.html', {'project': project})

        # Create Land objects
        lands_to_create = []
        for land_data in lands_data:
            land = Land(
                manual_id=land_data['manual_id'],
                block=land_data['block'],
                length=land_data['length'],
                width=land_data['width'],
                price=land_data['price'],
                currency=land_data['currency'],
                type=land_data['type'],
                status=land_data['status'],
                notes=land_data['notes'],
                project=project,
            )
            lands_to_create.append(land)

        # Bulk create all lands
        try:
            Land.objects.bulk_create(lands_to_create)
            messages.success(
                request,
                f'Se crearon exitosamente {len(lands_to_create)} terreno(s) para el proyecto {project.name}.'
            )
            return redirect('projects:detail', project_id=project.id)
        except Exception as e:
            messages.error(request, f'Error al guardar los terrenos: {str(e)}')
            return render(request, 'lands/create_multiple.html', {'project': project})

    # GET request
    return render(request, 'lands/create_multiple.html', {'project': project})

@login_required
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

@login_required
def delete(request, land_id):
    """
    Render the delete confirmation page for a specific land.
    """
    land = get_object_or_404(Land, pk=land_id)
    if request.method == 'POST':
        land.delete()
        return redirect(reverse("lands:index"))
    
    return render(request, 'lands/delete.html', {'land': land})

@login_required
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