# Generated by Django 5.1.5 on 2025-02-02 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roomie_property', '0002_property_deposit_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='deposit_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
    ]
