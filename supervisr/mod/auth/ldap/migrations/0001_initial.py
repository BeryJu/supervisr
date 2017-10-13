# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-20 14:29
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models

import supervisr.core.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('supervisr/core', '0057_auto_20170818_1943'),
    ]

    operations = [
        migrations.CreateModel(
            name='LDAPModification',
            fields=[
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('ldap_moddification_id', models.AutoField(primary_key=True, serialize=False)),
                ('dn', models.CharField(max_length=255)),
                ('action', models.CharField(choices=[('ADD', 'ADD'), ('MODIFY', 'MODIFY')], default='MODIFY', max_length=17)),
                ('data', supervisr.core.fields.JSONField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductExtensionLDAP',
            fields=[
                ('productextension_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervisr/core.ProductExtension')),
                ('ldap_group', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr/core.productextension',),
        ),
    ]
