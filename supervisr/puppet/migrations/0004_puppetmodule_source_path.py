# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-18 18:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr/puppet', '0003_auto_20170416_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='puppetmodule',
            name='source_path',
            field=models.TextField(blank=True, default=''),
        ),
    ]
