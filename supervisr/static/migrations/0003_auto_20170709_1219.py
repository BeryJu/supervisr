# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-09 10:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr/static', '0002_filepage'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticpage',
            name='has_html_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='staticpage',
            name='has_markdown_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='staticpage',
            name='listed',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='staticpage',
            name='views',
            field=models.BigIntegerField(default=0),
        ),
    ]