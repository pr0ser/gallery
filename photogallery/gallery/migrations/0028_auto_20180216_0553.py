# Generated by Django 2.0.1 on 2018-02-16 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0027_auto_20180215_2231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exifdata',
            name='lens',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Lens'),
        ),
    ]
