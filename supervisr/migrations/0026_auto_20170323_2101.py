# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-23 20:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr', '0025_add_settings_branding_icon_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=65),
        ),
    ]
