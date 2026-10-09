import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("investments", "0003_alter_investment_exchange_rate"),
        ("projects", "0004_project_installment_plans"),
    ]

    operations = [
        migrations.AlterField(
            model_name="investment",
            name="project",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="projects.project"),
        ),
    ]
