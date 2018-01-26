# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-16 17:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr_core', '0017_adjust_password_filter'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='ldap_group',
            field=models.TextField(blank=True, help_text='This is an optional field for a LDAP Group DN, to which the user is added once they have a relationship with the Product.'),
        ),
    ]
