# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-28 17:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0052_auto_20170726_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='auto_generated',
            field=models.BooleanField(default=True),
        ),
    ]
