# Generated by Django 5.1.5 on 2025-01-28 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cash_flow', '0006_remove_propertybilling_property_cash_flow'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='propertybilling',
            name='property_payment',
        ),
    ]
