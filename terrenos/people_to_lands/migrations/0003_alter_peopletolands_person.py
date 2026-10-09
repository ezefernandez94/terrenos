import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0002_alter_people_type"),
        ("people_to_lands", "0002_alter_peopletolands_options_peopletolands_land_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="peopletolands",
            name="person",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="people.people"),
        ),
    ]
