# Generated by Django 5.1.5 on 2025-02-15 11:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roomie_property', '0009_propertytenantrecords_tenant_request'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='propertytenantrecords',
            name='tenant_request',
        ),
    ]
