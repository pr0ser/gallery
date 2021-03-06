# Generated by Django 2.0.2 on 2018-02-13 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0015_auto_20180213_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exifdata',
            name='aperture',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True, verbose_name='Aperture'),
        ),
        migrations.AlterField(
            model_name='exifdata',
            name='has_location',
            field=models.BooleanField(default=False, verbose_name='Has location'),
        ),
    ]
