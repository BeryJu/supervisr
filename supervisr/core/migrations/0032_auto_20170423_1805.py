# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-23 16:05
from __future__ import unicode_literals

from django.db import migrations

from supervisr.core.models import get_system_user


def create_module(apps, schema_editor):
    PuppetModule = apps.get_model('supervisr/puppet', 'PuppetModule')
    User = apps.get_model('supervisr/core', 'User')
    system_user = User.objects.get(pk=get_system_user())

    PuppetModule.objects.get_or_create(
        name='supervisr_core',
        owner=system_user,
        source_path='supervisr/core/server/config/')

def create_userprofile(apps, schema_editor):
    User = apps.get_model('supervisr/core', 'User')
    UserProfile = apps.get_model('supervisr/core', 'UserProfile')
    system_user = User.objects.get(pk=get_system_user())

    UserProfile.objects.get_or_create(
        user=system_user)

class Migration(migrations.Migration):

    dependencies = [
        ('supervisr/core', '0031_remove_userprofile__purgeable'),
    ]

    operations = [
        migrations.RunPython(create_module),
        migrations.RunPython(create_userprofile),
    ]
