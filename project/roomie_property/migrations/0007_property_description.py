# Generated by Django 5.1.5 on 2025-02-05 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roomie_property', '0006_property_air_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
