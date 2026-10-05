from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0002_project_public_map"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="Identificador en la URL pública (/proyectos/<slug>/). Si se deja vacío se genera desde el nombre.",
                max_length=120,
                unique=True,
            ),
        ),
    ]
