# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-04 16:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr/mail', '0004_auto_20170202_2116'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mailaccount',
            name='password_salt',
        ),
    ]
