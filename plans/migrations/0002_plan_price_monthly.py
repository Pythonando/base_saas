from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("plans", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="plan",
            name="price_monthly",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]


