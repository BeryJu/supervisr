# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-31 19:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr/core', '0004_userproductrelationship_instance_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='management_url',
            field=models.URLField(blank=True, max_length=1000, null=True),
        ),
    ]
