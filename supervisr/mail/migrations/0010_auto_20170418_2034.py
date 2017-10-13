# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-18 18:34
from __future__ import unicode_literals

from django.db import migrations

from supervisr.core.models import get_system_user


def create_module(apps, schema_editor):
    PuppetModule = apps.get_model('supervisr/puppet', 'PuppetModule')
    User = apps.get_model('auth', 'User')
    system_user = User.objects.get(pk=get_system_user())

    PuppetModule.objects.get_or_create(
        name='supervisr_mail',
        owner=system_user,
        source_path='supervisr/mail/server/config/')

class Migration(migrations.Migration):

    dependencies = [
        ('supervisr/puppet', '0004_puppetmodule_source_path'),
        ('supervisr/mail', '0009_maildomain_enabled'),
    ]

    operations = [
        migrations.RunPython(create_module),
    ]
