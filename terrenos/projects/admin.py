from django import forms
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from .lot_map import SvgError, consistency_report, sanitize_svg
from .models import Project


class ProjectAdminForm(forms.ModelForm):
    """Project form with an SVG upload that is sanitized into Project.map_svg."""

    map_svg_file = forms.FileField(
        label="Subir plano (SVG)",
        required=False,
        help_text="Reemplaza el plano actual. Se eliminan scripts, imágenes, links externos y el grupo 'calco'. "
                  "Ver docs/mapa-interactivo.md para las convenciones de dibujo.",
    )
    clear_map_svg = forms.BooleanField(label="Quitar el plano actual", required=False)

    class Meta:
        model = Project
        exclude = ["map_svg"]

    def clean_map_svg_file(self):
        upload = self.cleaned_data.get("map_svg_file")
        if not upload:
            return None
        if not upload.name.lower().endswith(".svg"):
            raise forms.ValidationError("El archivo debe tener extensión .svg.")
        try:
            return sanitize_svg(upload.read())
        except SvgError as exc:
            raise forms.ValidationError(str(exc))

    def save(self, commit=True):
        project = super().save(commit=False)
        if self.cleaned_data.get("map_svg_file"):
            project.map_svg = self.cleaned_data["map_svg_file"]
        elif self.cleaned_data.get("clear_map_svg"):
            project.map_svg = ""
        if commit:
            project.save()
        return project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ["name", "slug", "is_public", "has_map", "public_link"]
    list_filter = ["is_public"]
    search_fields = ["name", "slug"]
    readonly_fields = ["map_report", "map_preview"]
    fieldsets = [
        (None, {"fields": ["name", "start_date", "end_date"]}),
        ("Web pública", {"fields": ["slug", "is_public"]}),
        ("Plano interactivo", {"fields": ["map_svg_file", "clear_map_svg", "map_report", "map_preview"]}),
    ]

    @admin.display(boolean=True, description="Plano")
    def has_map(self, obj):
        return bool(obj.map_svg)

    @admin.display(description="Página pública")
    def public_link(self, obj):
        if not obj.is_public:
            return "—"
        url = reverse("public_projects:detail", args=[obj.slug])
        return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', url, url)

    @admin.display(description="Reporte de consistencia")
    def map_report(self, obj):
        if not obj or not obj.pk:
            return "Guardá el proyecto para ver el reporte."
        report = consistency_report(obj)
        if not report["has_svg"]:
            return "Este proyecto no tiene plano cargado. La página pública mostrará sólo el listado de lotes."

        items = []
        if not report["has_lots_group"]:
            items.append(format_html(
                '<li style="color:#b45309">El SVG no tiene un grupo con id="lotes": ningún lote será interactivo.</li>'
            ))
        items.append(format_html("<li>Formas de lote en el SVG: <b>{}</b></li>", report["shape_count"]))
        if report["duplicate_shapes"]:
            items.append(format_html(
                '<li style="color:#b45309">IDs repetidos en el SVG: {}</li>', ", ".join(report["duplicate_shapes"])
            ))
        if report["orphan_shapes"]:
            items.append(format_html(
                '<li style="color:#b45309">Formas sin terreno asociado ({}): {}</li>',
                len(report["orphan_shapes"]), ", ".join(report["orphan_shapes"]),
            ))
        if report["lands_without_shape"]:
            lands = format_html_join(
                ", ", '<a href="{}">{} (mz. {}){}</a>',
                (
                    (
                        reverse("admin:lands_land_change", args=[land.pk]),
                        land.manual_id,
                        land.block,
                        f" — «{land.shape_id}» no está en el SVG" if land.shape_id else "",
                    )
                    for land in report["lands_without_shape"]
                ),
            )
            items.append(format_html(
                '<li style="color:#b45309">Terrenos sin forma en el plano ({}): {}</li>',
                len(report["lands_without_shape"]), lands,
            ))
        if not (report["orphan_shapes"] or report["lands_without_shape"] or report["duplicate_shapes"]):
            items.append(format_html('<li style="color:#047857">Todo coincide: cada terreno tiene su forma.</li>'))
        return format_html('<ul style="margin:0;padding-left:1.2em">{}</ul>', mark_safe("".join(items)))

    @admin.display(description="Vista previa")
    def map_preview(self, obj):
        if not obj or not obj.map_svg:
            return "—"
        ## map_svg only ever holds output of sanitize_svg(), so it is safe to inline
        return format_html(
            '<div style="max-width:640px;max-height:480px;overflow:auto;border:1px solid #ccc;background:#fff">{}</div>',
            mark_safe(obj.map_svg),
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if form.cleaned_data.get("map_svg_file"):
            report = consistency_report(obj)
            problems = len(report["orphan_shapes"]) + len(report["lands_without_shape"]) + len(report["duplicate_shapes"])
            if problems or not report["has_lots_group"]:
                messages.warning(
                    request,
                    "Plano guardado con advertencias: revisá el reporte de consistencia en la sección «Plano interactivo».",
                )
            else:
                messages.success(request, "Plano guardado. Todos los terrenos tienen su forma en el SVG.")
