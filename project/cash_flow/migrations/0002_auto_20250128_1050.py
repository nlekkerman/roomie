from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cash_flow', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertypayments',
            name='deadline',
            field=models.DateField(null=True, blank=True),
        ),
    ]
