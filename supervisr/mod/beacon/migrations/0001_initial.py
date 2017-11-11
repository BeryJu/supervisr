# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-10 19:39
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pulse',
            fields=[
                ('pulse_id', models.AutoField(primary_key=True, serialize=False)),
                ('install_id', models.UUIDField(verbose_name="Installation's unique ID")),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('python_version', models.CharField(max_length=100)),
                ('os_uname', models.CharField(max_length=255)),
                ('user_count', models.BigIntegerField(verbose_name='Approximate user count')),
                ('domain_count', models.BigIntegerField(verbose_name='Approximate domain count')),
            ],
        ),
        migrations.CreateModel(
            name='PulseModule',
            fields=[
                ('pulse_module_id', models.AutoField(primary_key=True, serialize=False)),
                ('module_root', models.TextField()),
                ('name', models.TextField()),
                ('author', models.TextField()),
                ('author_email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='PulseModuleVersion',
            fields=[
                ('pulse_module_version_id', models.AutoField(primary_key=True, serialize=False)),
                ('version', models.TextField()),
                ('pulse_module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr/mod/beacon.PulseModule')),
            ],
        ),
        migrations.AddField(
            model_name='pulse',
            name='modules',
            field=models.ManyToManyField(to='supervisr/mod/beacon.PulseModule'),
        ),
    ]
