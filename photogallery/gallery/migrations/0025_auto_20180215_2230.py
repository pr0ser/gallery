# Generated by Django 2.0.1 on 2018-02-15 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0024_auto_20180215_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exifdata',
            name='shutter_speed',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Shutter speed'),
            preserve_default=False,
        ),
    ]
