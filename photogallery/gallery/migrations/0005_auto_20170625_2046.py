# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-25 20:46
from __future__ import unicode_literals

from django.db import migrations, models
import gallery.models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0004_photo_ready'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='title',
            field=models.CharField(max_length=255, unique=True, validators=[gallery.models.validate_photo_title], verbose_name='Title'),
        ),
    ]
