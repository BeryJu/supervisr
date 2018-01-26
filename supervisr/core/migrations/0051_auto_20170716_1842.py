# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-16 16:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('supervisr_core', '0050_auto_20170707_1121'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='providerinstance',
            name='credentials',
        ),
        migrations.DeleteModel(
            name='ProviderInstance',
        ),
        migrations.RenameModel(
            old_name='BaseProviderInstance',
            new_name='ProviderInstance',
        ),
    ]
