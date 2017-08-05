# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-26 13:15
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0051_auto_20170716_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domains', to='core.ProviderInstance'),
        ),
    ]
