# Generated by Django 5.1.5 on 2025-01-28 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cash_flow', '0002_auto_20250128_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertypayments',
            name='help_text',
            field=models.DateField(blank=True, null=True),
        ),
    ]
