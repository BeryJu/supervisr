# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-15 10:47
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PuppetModule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('downloads', models.IntegerField(default=0)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('supported', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PuppetModuleRelease',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.TextField()),
                ('release', models.FileField(upload_to='')),
                ('downloads', models.IntegerField(default=0)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('readme', models.TextField(blank=True)),
                ('changelog', models.TextField(blank=True)),
                ('license', models.TextField(blank=True)),
                ('metadata', models.TextField()),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr_puppet.PuppetModule')),
            ],
        ),
        migrations.CreateModel(
            name='PuppetUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.TextField()),
                ('display_name', models.TextField()),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='puppetmodule',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr_puppet.PuppetUser'),
        ),
    ]
