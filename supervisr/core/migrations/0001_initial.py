# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-30 23:47
from __future__ import unicode_literals

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import supervisr.core.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '__latest__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('crypt6_password', models.CharField(blank=True, default='', max_length=128)),
                ('unix_username', models.CharField(default=supervisr.core.models.get_random_string, editable=False, max_length=32)),
                ('unix_userid', models.IntegerField(default=supervisr.core.models.get_userid)),
                ('locale', models.CharField(default='en-US', max_length=5)),
                ('news_subscribe', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
                ('rows_per_page',models.IntegerField(default=50),),
                ('theme', models.CharField(default='light', max_length=200)),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AccountConfirmation',
            fields=[
                ('account_confirmation_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('expires', models.BigIntegerField(default=supervisr.core.models.expiry_date, editable=False)),
                ('confirmed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HostedApplicationProduct',
            fields=[
                ('hosted_application_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('version', models.TextField()),
                ('developer', models.TextField()),
                ('developer_site', models.URLField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='IPAddress',
            fields=[
                ('ipaddress_id', models.AutoField(primary_key=True, serialize=False)),
                ('address', models.GenericIPAddressField()),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('notification_id', models.AutoField(primary_key=True, serialize=False)),
                ('destination_link', models.TextField()),
                ('importance', models.IntegerField(choices=[(40, 'Urgent'), (30, 'Important'), (20, 'Medium'), (10, 'Information (Semi-medium)'), (0, 'Information')], default=0)),
                ('read', models.BooleanField(default=False)),
                ('destination_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_notifications', to=settings.AUTH_USER_MODEL)),
                ('source_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('slug', models.TextField()),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=3, max_digits=65)),
                ('invite_only', models.BooleanField(default=False)),
                ('managed', models.BooleanField(default=True)),
                ('management_url', models.URLField(default='', max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='ServerCPU',
            fields=[
                ('cpu_id', models.AutoField(primary_key=True, serialize=False)),
                ('physical_cores', models.IntegerField()),
                ('smt', models.BooleanField()),
                ('frequency', models.IntegerField(default=0)),
                ('make', models.TextField()),
                ('model', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ServerDrive',
            fields=[
                ('drive_id', models.AutoField(primary_key=True, serialize=False)),
                ('capacity', models.IntegerField()),
                ('make', models.TextField()),
                ('model', models.TextField()),
                ('rpm', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ServerNIC',
            fields=[
                ('nic_id', models.AutoField(primary_key=True, serialize=False)),
                ('speed', models.IntegerField()),
                ('ips', models.ManyToManyField(blank=True, to='supervisr/core.IPAddress')),
            ],
        ),
        migrations.CreateModel(
            name='UserProductRelationship',
            fields=[
                ('user_product_relationship_id', models.AutoField(primary_key=True, serialize=False)),
                ('expiry_delta', models.BigIntegerField(default=0)),
                ('discount_percent', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ServerProduct',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='supervisr/core.Product')),
                ('server_id', models.AutoField(primary_key=True, serialize=False)),
                ('ram', models.IntegerField()),
                ('is_virtual', models.BooleanField(default=True)),
                ('is_managed', models.BooleanField(default=True)),
                ('cpus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr/core.ServerCPU')),
                ('drives', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr/core.ServerDrive')),
                ('nics', models.ManyToManyField(to='supervisr/core.ServerNIC')),
            ],
        ),
        migrations.AddField(
            model_name='userproductrelationship',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr/core.Product'),
        ),
        migrations.AddField(
            model_name='userproductrelationship',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='product',
            name='users',
            field=models.ManyToManyField(through='supervisr/core.UserProductRelationship', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='hostedapplicationproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr/core.Product'),
        ),
    ]
