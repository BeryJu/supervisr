# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-18 20:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr', '0002_auto_20160924_1244'),
    ]

    operations = [
        migrations.AddField(
            model_name='serverproduct',
            name='name',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
    ]