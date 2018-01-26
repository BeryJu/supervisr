# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-26 13:19
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('supervisr_core', '0052_auto_20170726_1515'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebDomain',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervisr_core.Product')),
                ('root', models.TextField(default='/')),
                ('quota', models.BigIntegerField(default=0)),
                ('is_php_enabled', models.BooleanField(default=True)),
                ('custom_config', models.TextField(blank=True)),
                ('domain_web', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='supervisr_core.Domain')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr_core.UserProfile')),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_core.product',),
        ),
    ]
