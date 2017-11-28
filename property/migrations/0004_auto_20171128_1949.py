# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-28 19:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0003_auto_20171127_2336'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='property',
            name='community',
        ),
        migrations.AddField(
            model_name='property',
            name='neighborhood',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='property',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9),
        ),
        migrations.AlterField(
            model_name='property',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9),
        ),
        migrations.AlterField(
            model_name='property',
            name='postal_code',
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AlterField(
            model_name='property',
            name='region',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
