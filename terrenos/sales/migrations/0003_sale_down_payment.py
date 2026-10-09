from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0002_sale_land"),
    ]

    operations = [
        migrations.AddField(
            model_name="sale",
            name="down_payment",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="sale",
            name="down_payment_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
