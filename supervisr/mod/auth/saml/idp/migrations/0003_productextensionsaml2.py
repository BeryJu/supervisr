# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-30 16:50
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr_core', '0052_auto_20170726_1515'),
        ('supervisr_mod_auth_saml_idp', '0002_auto_20170729_1623'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductExtensionSAML2',
            fields=[
                ('productextension_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervisr_core.ProductExtension')),
                ('saml_remote', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr_mod_auth_saml_idp.SAMLRemote')),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_core.productextension',),
        ),
    ]
