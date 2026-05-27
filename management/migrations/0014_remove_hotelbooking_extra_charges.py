from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0013_hotelpayment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hotelbooking',
            name='extra_charges',
        ),
    ]
