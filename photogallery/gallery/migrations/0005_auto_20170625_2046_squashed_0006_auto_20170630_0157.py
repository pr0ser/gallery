# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-30 02:10
from __future__ import unicode_literals

from django.db import migrations, models
import gallery.models


class Migration(migrations.Migration):

    replaces = [('gallery', '0005_auto_20170625_2046'), ('gallery', '0006_auto_20170630_0157')]

    dependencies = [
        ('gallery', '0004_photo_ready'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='title',
            field=models.CharField(max_length=255, unique=True, validators=[gallery.models.validate_photo_title], verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='title',
            field=models.CharField(max_length=255, unique=True, verbose_name='Title'),
        ),
    ]
