# Generated by Django 5.1.5 on 2025-02-05 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roomie_user', '0002_customuser_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_owner',
            field=models.BooleanField(default=False),
        ),
    ]
