# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-20 19:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr_mod_ldap', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ldapmodification',
            name='action',
        ),
        migrations.AlterField(
            model_name='ldapmodification',
            name='data',
            field=models.TextField(),
        ),
    ]