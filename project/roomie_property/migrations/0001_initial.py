# Generated by Django 5.1.5 on 2025-01-27 20:07

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(max_length=255)),
                ('house_number', models.CharField(max_length=20)),
                ('town', models.CharField(max_length=100)),
                ('county', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
                ('property_rating', models.DecimalField(decimal_places=1, default=5.0, max_digits=3)),
                ('room_capacity', models.PositiveIntegerField()),
                ('people_capacity', models.PositiveIntegerField()),
                ('rent_amount', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_properties', to=settings.AUTH_USER_MODEL)),
                ('property_supervisor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='supervised_properties', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PropertyTenantRecords',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tenant_history', to='roomie_property.property')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tenant_history', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
