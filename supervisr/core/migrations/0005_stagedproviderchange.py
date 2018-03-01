# Generated by Django 2.0.2 on 2018-03-01 16:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr_core', '0004_auto_20180225_1403'),
    ]

    operations = [
        migrations.CreateModel(
            name='StagedProviderChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('model_path', models.TextField(help_text='Django-style path, <app_label>.<model_name>')),
                ('action', models.CharField(choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')], max_length=20)),
                ('body', models.TextField(help_text='This data is directly passed to the marshall as arg.')),
                ('provider_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr_core.ProviderInstance')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
