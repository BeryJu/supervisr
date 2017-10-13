# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-31 13:56
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr/core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serverproduct',
            name='product_ptr',
        ),
        migrations.AddField(
            model_name='serverproduct',
            name='name',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='serverproduct',
            name='product',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='supervisr/core.Product'),
            preserve_default=False,
        ),
    ]
