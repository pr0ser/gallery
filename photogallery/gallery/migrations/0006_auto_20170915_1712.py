# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-15 17:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0005_auto_20170625_2046_squashed_0006_auto_20170630_0157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='slug',
            field=models.SlugField(max_length=100, unique=True, verbose_name='Slug'),
        ),
    ]
