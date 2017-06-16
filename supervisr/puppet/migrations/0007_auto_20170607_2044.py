# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-07 18:44
from __future__ import unicode_literals

from django.db import migrations


def create_setting(apps, schema_editor):
    Setting = apps.get_model('core', 'Setting')
    Setting.objects.get_or_create(
        key='puppet:allowed_user_agent',
        defaults={'value': ''})

class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '0006_auto_20170503_1821'),
    ]

    operations = [
        migrations.RunPython(create_setting),
    ]