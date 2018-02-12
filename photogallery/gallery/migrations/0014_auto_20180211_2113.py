# Generated by Django 2.0.2 on 2018-02-11 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0013_auto_20180209_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exifdata',
            name='lens',
            field=models.CharField(max_length=200, null=True, verbose_name='Lens'),
        ),
        migrations.AlterField(
            model_name='exifdata',
            name='make',
            field=models.CharField(max_length=100, null=True, verbose_name='Manufacturer'),
        ),
        migrations.AlterField(
            model_name='exifdata',
            name='model',
            field=models.CharField(max_length=100, null=True, verbose_name='Model'),
        ),
        migrations.AlterField(
            model_name='exifdata',
            name='shutter_speed',
            field=models.CharField(max_length=50, null=True, verbose_name='Shutter speed'),
        ),
    ]
