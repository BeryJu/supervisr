# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-31 19:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr/core', '0003_auto_20161231_1824'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproductrelationship',
            name='instance_name',
            field=models.TextField(blank=True, null=True),
            preserve_default=False,
        ),
    ]
