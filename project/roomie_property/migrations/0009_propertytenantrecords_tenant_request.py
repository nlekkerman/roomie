# Generated by Django 5.1.5 on 2025-02-13 17:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roomie_property', '0008_tenancyrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertytenantrecords',
            name='tenant_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='roomie_property.tenancyrequest'),
        ),
    ]
