# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-12 18:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


def create_settings(apps, schema_editor):
    Setting = apps.get_model('supervisr/core', 'Setting')
    settings = {
        'core:recaptcha:private': '',
        'core:recaptcha:public': '',
        'core:domain': 'http://localhost/',
        'core:branding': 'supervisr',
    }
    for key, value in settings.items():
        Setting.objects.get_or_create(
            key=key,
            defaults={'value': value})

def create_user(apps, schema_editor):
    User = apps.get_model('supervisr/core', 'User')
    system_user = User.objects.get_or_create(
        username=settings.SYSTEM_USER_NAME,
        is_active=False,
        is_staff=False,
        is_superuser=False,
        first_name='System',
        defaults={'email': 'root@localhost'})

class Migration(migrations.Migration):

    dependencies = [
        ('supervisr/core', '0012_event'),
    ]

    operations = [
        migrations.RunPython(create_settings),
        migrations.RunPython(create_user),
    ]
