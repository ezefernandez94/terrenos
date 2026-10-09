import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lands", "0004_land_map_fields"),
        ("projects", "0004_project_installment_plans"),
    ]

    operations = [
        migrations.AlterField(
            model_name="land",
            name="project",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="projects.project"),
        ),
        migrations.AlterField(
            model_name="land",
            name="seller",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="sellers.seller"),
        ),
    ]
