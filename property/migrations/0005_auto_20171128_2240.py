# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-28 22:40
from __future__ import unicode_literals

from django.db import migrations, models
import property.models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0004_auto_20171128_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='postal_code',
            field=models.CharField(max_length=6, validators=[property.models.validate_postal_code]),
        ),
        migrations.AlterField(
            model_name='property',
            name='publish_stamp',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='publish time'),
        ),
    ]