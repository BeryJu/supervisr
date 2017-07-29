# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-07 20:04
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

from supervisr.core.models import get_system_user


def create_default_pages(apps, schema_editor):
    names = ['CHANGELOG.md', 'ATTRIBUTIONS.md']
    FilePage = apps.get_model('supervisr/static', 'FilePage')
    User = apps.get_model('auth', 'User')
    sys_user = User.objects.get(pk=get_system_user())
    for name in names:
        b_name = name.split('.')[0]
        FilePage.objects.create(
            title=b_name.title(),
            slug=b_name.lower(),
            path=name,
            author=sys_user,
            published=True)

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0013_auto_20170112_1925'),
        ('supervisr/static', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilePage',
            fields=[
                ('staticpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervisr/static.StaticPage')),
                ('path', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr/static.staticpage',),
        ),
        migrations.RunPython(
            code=create_default_pages,
        ),
    ]
