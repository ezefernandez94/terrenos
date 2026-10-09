import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("projects", "0004_project_installment_plans"),
    ]

    operations = [
        migrations.CreateModel(
            name="Faq",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question", models.CharField(max_length=255)),
                ("answer", models.TextField()),
                ("question_en", models.CharField(blank=True, default="", max_length=255)),
                ("answer_en", models.TextField(blank=True, default="")),
                ("question_pt", models.CharField(blank=True, default="", max_length=255)),
                ("answer_pt", models.TextField(blank=True, default="")),
                ("order", models.PositiveIntegerField(default=0, help_text="Las preguntas se muestran de menor a mayor.")),
                ("is_published", models.BooleanField(default=True)),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="faqs",
                        to="projects.project",
                    ),
                ),
            ],
            options={
                "verbose_name": "Pregunta frecuente",
                "verbose_name_plural": "Preguntas frecuentes",
                "ordering": ["order", "id"],
            },
        ),
    ]
