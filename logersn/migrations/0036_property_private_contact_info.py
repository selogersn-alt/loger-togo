# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logersn', '0035_property_price_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='private_contact_info',
            field=models.TextField(blank=True, null=True, verbose_name='Contact agent / Note privée'),
        ),
    ]
