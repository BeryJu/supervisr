# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-27 16:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr_mail', '0005_remove_mailaccount_password_salt'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailaccount',
            name='size',
            field=models.BigIntegerField(default=0),
        ),
    ]