# Generated by Django 5.1.5 on 2025-01-28 18:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cash_flow', '0008_propertybilling_property_payment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='propertybilling',
            name='property_payment',
        ),
    ]
