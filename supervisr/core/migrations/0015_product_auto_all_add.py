# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-12 21:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr/core', '0014_auto_20170112_1934'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='auto_all_add',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='auto_add',
            field=models.BooleanField(default=False),
        ),
    ]
