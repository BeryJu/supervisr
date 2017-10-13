# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-16 13:50
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr/puppet', '0002_auto_20170415_1311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='puppetmodule',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='PuppetUser',
        ),
    ]
