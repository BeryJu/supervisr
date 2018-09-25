# Generated by Django 2.1.1 on 2018-09-25 10:28

import uuid

import django.db.models.deletion
from django.db import migrations, models

import supervisr.core.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('supervisr_core', '0001_initial'),
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='LDAPGroupMapping',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('ldap_dn', models.TextField()),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LDAPModification',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
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
                ('productextension_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervisr_core.ProductExtension')),
                ('ldap_group', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_core.productextension',),
        ),
    ]
