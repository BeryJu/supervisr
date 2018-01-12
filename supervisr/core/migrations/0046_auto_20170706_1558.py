# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-06 13:58
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr_core', '0045_auto_20170706_1335'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='BaseProviderInstance',
            name='user',
        ),
        migrations.AddField(
            model_name='BaseProviderInstance',
            name='credentials',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='supervisr_core.BaseCredential'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='BaseProviderInstance',
            name='provider',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
    ]
