# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logersn', '0037_property_private_contact_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='internal_ref',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Référence source'),
        ),
    ]
