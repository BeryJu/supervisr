# Generated by Django 2.1.1 on 2018-09-25 10:28

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('supervisr_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebApplication',
            fields=[
                ('useracquirable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='supervisr_core.UserAcquirable')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('upstream', models.URLField()),
                ('access_slug', models.SlugField()),
                ('add_remote_user', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_core.useracquirable', models.Model),
        ),
    ]
