from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):
    dependencies = [
        ("quotes", "0005_quote_deposit_amount_quote_deposit_percentage_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="quoterevision",
            name="previous_deposit_required",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="quoterevision",
            name="new_deposit_required",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="quoterevision",
            name="previous_deposit_amount",
            field=models.DecimalField(
                max_digits=10, decimal_places=2, default=Decimal("0.00")
            ),
        ),
        migrations.AddField(
            model_name="quoterevision",
            name="new_deposit_amount",
            field=models.DecimalField(
                max_digits=10, decimal_places=2, default=Decimal("0.00")
            ),
        ),
    ]
