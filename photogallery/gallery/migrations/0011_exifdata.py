# Generated by Django 2.0.1 on 2018-02-09 18:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0010_auto_20170924_2141'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExifData',
            fields=[
                ('photo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='gallery.Photo')),
                ('date_taken', models.DateTimeField(verbose_name='Date/Time taken')),
                ('has_location', models.BooleanField(default=False)),
                ('make', models.CharField(max_length=100, verbose_name='Manufacturer')),
                ('model', models.CharField(max_length=100, verbose_name='Model')),
                ('iso', models.PositiveIntegerField(verbose_name='ISO speed')),
                ('shutter_speed', models.CharField(max_length=10, verbose_name='Shutter speed')),
                ('aperture', models.DecimalField(decimal_places=1, max_digits=3, verbose_name='Focal length')),
                ('focal_length', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Focal length')),
                ('lens', models.CharField(max_length=200, verbose_name='Lens')),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Latitude')),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Longitude')),
                ('altitude', models.PositiveIntegerField(verbose_name='Altitude')),
            ],
        ),
    ]