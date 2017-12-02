# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-02 10:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr/core', '0061_auto_20171118_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='rows_per_page',
            field=models.IntegerField(default=50),
        ),
        migrations.AddField(
            model_name='user',
            name='theme',
            field=models.CharField(default='light', max_length=200),
        ),
    ]
