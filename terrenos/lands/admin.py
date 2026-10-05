from django import forms
from django.contrib import admin
from django.forms.models import BaseModelFormSet
from .models import Land

DUPLICATE_SHAPE_ID = "Ya hay otro terreno de este proyecto con el shape ID «%(shape_id)s»."


class LandAdminForm(forms.ModelForm):
    """
    Checks shape_id uniqueness per project explicitly: on the changelist the form has no
    'project' field, so Django skips the (project, shape_id) constraint and the DB would raise.
    """

    def clean(self):
        cleaned = super().clean()
        shape_id = cleaned.get("shape_id", self.instance.shape_id)
        project = cleaned.get("project") or (self.instance.project if self.instance.project_id else None)
        if shape_id and project:
            taken = Land.objects.filter(project=project, shape_id=shape_id).exclude(pk=self.instance.pk)
            if taken.exists():
                self.add_error("shape_id", DUPLICATE_SHAPE_ID % {"shape_id": shape_id})
        return cleaned


class LandChangelistFormSet(BaseModelFormSet):
    """Rejects the same shape_id typed twice for one project in a single changelist save."""

    def clean(self):
        super().clean()
        seen = set()
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or not form.cleaned_data.get("shape_id"):
                continue
            key = (form.instance.project_id, form.cleaned_data["shape_id"])
            if key in seen:
                form.add_error("shape_id", DUPLICATE_SHAPE_ID % {"shape_id": key[1]})
            seen.add(key)


# Register the Land model with the admin site
@admin.register(Land)
class LandAdmin(admin.ModelAdmin):
    form = LandAdminForm
    list_display = ["__str__", "project", "block", "manual_id", "status", "price", "currency", "shape_id"]
    ## shape_id is editable from the list so a whole project can be linked to its SVG quickly
    list_editable = ["shape_id"]
    list_filter = ["project", "status", "block"]
    search_fields = ["manual_id", "block", "shape_id"]
    fieldsets = [
        (None, {"fields": ["project", "manual_id", "block", "width", "length", "type"]}),
        ("Venta", {"fields": ["price", "currency", "status", "seller", "notes"]}),
        ("Plano interactivo", {"fields": ["shape_id", ("label_x", "label_y")]}),
    ]

    def get_changelist_form(self, request, **kwargs):
        kwargs.setdefault("form", LandAdminForm)
        return super().get_changelist_form(request, **kwargs)

    def get_changelist_formset(self, request, **kwargs):
        kwargs.setdefault("formset", LandChangelistFormSet)
        return super().get_changelist_formset(request, **kwargs)
