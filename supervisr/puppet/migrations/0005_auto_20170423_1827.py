# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-23 16:27
from __future__ import unicode_literals

from django.db import migrations

from supervisr.core.models import get_system_user


def create_module(apps, schema_editor):
    User = apps.get_model('supervisr/core', 'User')
    Group = apps.get_model('auth', 'Group')
    system_user = User.objects.get(pk=get_system_user())

    ps_group = Group.objects.get_or_create(
        name='Puppet Systemusers')[0]
    ps_group.user_set.add(system_user)
    for user in User.objects.filter(is_superuser=True):
        ps_group.user_set.add(user)

class Migration(migrations.Migration):

    dependencies = [
        ('supervisr/core', '0013_auto_20170112_1925'),
        ('supervisr/puppet', '0004_puppetmodule_source_path'),
    ]

    operations = [
        migrations.RunPython(create_module),
    ]
