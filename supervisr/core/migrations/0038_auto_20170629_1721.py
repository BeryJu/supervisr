# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-29 15:21
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


def update_domains(apps, schema_editor):
    Domain = apps.get_model('core', 'Domain')
    for domain in Domain.objects.all():
        domain.domain = domain.name
        domain.name = 'Domain %s' % domain.domain
        domain.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_auto_20170610_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='domain',
            field=models.CharField(max_length=253, default='None', unique=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='domain',
            name='product_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='domains', serialize=False, to='core.Product'),
        ),
        migrations.RunPython(update_domains),
        migrations.AlterField(
            model_name='domain',
            name='domain',
            field=models.CharField(max_length=253, unique=True),
        ),
    ]
