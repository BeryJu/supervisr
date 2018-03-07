# Generated by Django 2.0.2 on 2018-03-02 18:52

import django.db.models.deletion
from django.db import migrations, models

import supervisr.core.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
        ('supervisr_core', '0007_auto_20180302_1849'),
    ]

    operations = [
        migrations.CreateModel(
            name='LDAPGroupMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('productextension_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervisr_core.ProductExtension')),
                ('ldap_group', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_core.productextension',),
        ),
    ]
