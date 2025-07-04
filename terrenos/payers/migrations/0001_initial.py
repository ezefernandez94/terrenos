# Generated by Django 4.2.23 on 2025-06-26 16:57

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Payer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("notes", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Pagador",
                "verbose_name_plural": "Pagadores",
                "ordering": ["name"],
            },
        ),
    ]
