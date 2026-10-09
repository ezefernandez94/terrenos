from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0004_project_installment_plans"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="status",
            field=models.CharField(
                choices=[("coming_soon", "Próximamente"), ("in_progress", "En curso"), ("finished", "Finalizado")],
                default="in_progress",
                max_length=20,
            ),
        ),
    ]
