from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sales_summary", "0002_salesummary_amount_salesummary_sale"),
    ]

    operations = [
        migrations.AlterField(
            model_name="salesummary",
            name="type",
            field=models.CharField(
                choices=[
                    ("initial_payment", "Pago Inicial"),
                    ("monthly_payment", "Cuota"),
                    ("remaining_payment", "Pago de Saldo Restante"),
                ],
                default="monthly_payment",
                max_length=50,
            ),
        ),
    ]
