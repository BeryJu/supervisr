# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-02 15:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20170629_1804'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductExtensionOAuth2',
        ),
    ]
