from django.db import migrations, models
from django.utils.text import slugify


def fill_slugs(apps, schema_editor):
    ## Gives every existing project a unique slug derived from its name
    Project = apps.get_model("projects", "Project")
    used = set()
    for project in Project.objects.order_by("id"):
        base = slugify(project.name)[:110] or "proyecto"
        slug, n = base, 2
        while slug in used:
            slug, n = f"{base}-{n}", n + 1
        used.add(slug)
        project.slug = slug
        project.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        ## Added nullable first so existing rows are valid; made unique in 0003
        migrations.AddField(
            model_name="project",
            name="slug",
            field=models.SlugField(max_length=120, null=True, blank=True, db_index=False),
        ),
        migrations.AddField(
            model_name="project",
            name="is_public",
            field=models.BooleanField(
                default=False,
                help_text="Si está activo, el proyecto y su plano se muestran en la web pública.",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="map_svg",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Plano interactivo (SVG ya sanitizado). Se carga desde el admin.",
            ),
        ),
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
    ]
