# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-27 18:48
from __future__ import unicode_literals

import django.utils.timezone
from django.db import migrations, models


def create_settings(apps, schema_editor):
    Setting = apps.get_model('core', 'Setting')
    settings = {
        'core:analytics:ga:enabled': False,
        'core:analytics:ga:tracking_id': '',
    }
    for key, value in settings.items():
        Setting.objects.get_or_create(
            key=key,
            defaults={'value': value})

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_remove_domain_domain_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProviderInstance',
            fields=[
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('provider_instance_id', models.AutoField(primary_key=True, serialize=False)),
                ('provider_app', models.CharField(max_length=255)),
                ('provider_module', models.CharField(max_length=255)),
                ('provider_class', models.CharField(max_length=255)),
                ('provider_name', models.TextField()),
                ('is_managed', models.BooleanField(max_length=255)),
                ('user_id', models.TextField()),
                ('user_password', models.TextField()),
                ('salt', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='accountconfirmation',
            name='created',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='accountconfirmation',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='event',
            name='created',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='product',
            name='created',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='setting',
            name='created',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='setting',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='userproductrelationship',
            name='created',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userproductrelationship',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='created',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.RunPython(create_settings),
    ]
