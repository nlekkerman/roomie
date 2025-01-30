# Generated by Django 5.1.5 on 2025-01-30 13:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cash_flow', '0010_propertybilling_property_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercashflow',
            name='property_billing',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_cash_flows', to='cash_flow.propertybilling'),
        ),
    ]
