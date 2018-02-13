# Generated by Django 2.0.1 on 2018-02-09 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0012_auto_20180209_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exifdata',
            name='altitude',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Altitude'),
        ),
        migrations.AlterField(
            model_name='exifdata',
            name='aperture',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True, verbose_name='Focal length'),
        ),
        migrations.AlterField(
            model_name='exifdata',
            name='date_taken',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date/Time taken'),
        ),
        migrations.AlterField(
            model_name='exifdata',
            name='focal_length',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Focal length'),
        ),
        migrations.AlterField(
            model_name='exifdata',
            name='iso',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='ISO speed'),
        ),
        migrations.AlterField(
            model_name='exifdata',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Latitude'),
        ),
        migrations.AlterField(
            model_name='exifdata',
            name='lens',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Lens'),
        ),
        migrations.AlterField(
            model_name='exifdata',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Longitude'),
        ),
        migrations.AlterField(
            model_name='exifdata',
            name='make',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Manufacturer'),
        ),
        migrations.AlterField(
            model_name='exifdata',
            name='model',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Model'),
        ),
        migrations.AlterField(
            model_name='exifdata',
            name='shutter_speed',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Shutter speed'),
        ),
    ]