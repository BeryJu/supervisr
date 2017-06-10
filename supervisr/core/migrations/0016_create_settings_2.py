# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-13 13:43
from __future__ import unicode_literals

from django.db import migrations


def create_settings(apps, schema_editor):
    Setting = apps.get_model('core', 'Setting')
    settings = {
        'core:password:filter:description': 'One Letter, one Number and one speical Character',
        'core:password:filter': r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&\.])[A-Za-z\d$@$!%*?&\.]{8,}$",
    }
    for key, value in settings.items():
        Setting.objects.get_or_create(
            key=key,
            defaults={'value': value})

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_product_auto_all_add'),
    ]

    operations = [
        migrations.RunPython(create_settings),
    ]
