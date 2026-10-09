import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0003_alter_project_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="installment_plans",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.PositiveSmallIntegerField(
                    choices=[(12, "12 cuotas"), (24, "24 cuotas"), (36, "36 cuotas"), (48, "48 cuotas")]
                ),
                blank=True,
                default=list,
                help_text="Planes de cuotas que se muestran en la web pública.",
                size=None,
            ),
        ),
    ]
