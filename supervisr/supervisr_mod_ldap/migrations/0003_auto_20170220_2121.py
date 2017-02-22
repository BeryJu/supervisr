# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-20 20:21
from __future__ import unicode_literals

import django.utils.timezone
from django.db import migrations, models

import supervisr.fields


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr_mod_ldap', '0002_auto_20170220_2040'),
    ]

    operations = [
        migrations.AddField(
            model_name='ldapmodification',
            name='action',
            field=models.CharField(choices=[('ADD', 'ADD'), ('MODIFY', 'MODIFY')], default='MODIFY', max_length=17),
        ),
        migrations.AddField(
            model_name='ldapmodification',
            name='created',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ldapmodification',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='ldapmodification',
            name='data',
            field=supervisr.fields.JSONField(),
        ),
    ]
