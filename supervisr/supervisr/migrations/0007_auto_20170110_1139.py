# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-10 10:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr', '0006_setting'),
    ]

    operations = [
        migrations.RenameField(
            model_name='setting',
            old_name='value_json',
            new_name='value',
        ),
        migrations.AddField(
            model_name='accountconfirmation',
            name='kind',
            field=models.IntegerField(choices=[(0, 'Sign up'), (1, 'Password Reset')], default=0),
        ),
        migrations.AlterField(
            model_name='notification',
            name='importance',
            field=models.IntegerField(choices=[(40, 'Urgent'), (30, 'Important'), (20, 'Medium'), (10, 'Notice'), (0, 'Information')], default=0),
        ),
    ]
