# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-16 16:47
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr_core', '0051_auto_20170716_1842'),
        ('supervisr_mail', '0012_auto_20170715_2246'),
    ]

    operations = [
        migrations.AddField(
            model_name='maildomain',
            name='provider',
            field=models.ForeignKey(default=None, null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='supervisr_core.ProviderInstance'),
        ),
    ]
