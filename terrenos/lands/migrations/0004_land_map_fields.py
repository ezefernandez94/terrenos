from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lands", "0003_land_currency"),
        ("projects", "0003_alter_project_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="land",
            name="shape_id",
            field=models.CharField(
                blank=True,
                default="",
                help_text="ID de la forma del lote en el SVG del proyecto (ej. fr8-l3). Único dentro del proyecto.",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="land",
            name="label_x",
            field=models.FloatField(
                blank=True,
                null=True,
                help_text="Posición X de la etiqueta en coordenadas del SVG. Vacío = centro de la forma.",
            ),
        ),
        migrations.AddField(
            model_name="land",
            name="label_y",
            field=models.FloatField(
                blank=True,
                null=True,
                help_text="Posición Y de la etiqueta en coordenadas del SVG. Vacío = centro de la forma.",
            ),
        ),
        migrations.AddConstraint(
            model_name="land",
            constraint=models.UniqueConstraint(
                condition=models.Q(("shape_id", ""), _negated=True),
                fields=("project", "shape_id"),
                name="uniq_land_shape_id_per_project",
            ),
        ),
    ]
