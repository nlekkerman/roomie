# Generated by Django 5.1.5 on 2025-01-30 17:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cash_flow', '0016_alter_usercashflow_property_billing'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercashflow',
            name='tenant_billing',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_cash_flows', to='cash_flow.tenantbilling'),
        ),
    ]
