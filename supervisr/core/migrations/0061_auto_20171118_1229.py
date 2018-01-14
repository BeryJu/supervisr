# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-18 11:29
from __future__ import unicode_literals

import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models

import supervisr.core.models


def migrate_profile_data(apps, schema_editor):
    UserProfile = apps.get_model('supervisr_core', 'UserProfile')
    User = apps.get_model('supervisr_core', 'User')
    old_user_model = apps.get_model('auth', 'User')

    for old_user in old_user_model.objects.all():
       # simply copy the fields you need into the new user. the `id` is the most important field
       new_user = User.objects.create(
           id=old_user.id,   # this is a very important thing to do, because of the generic relations,
           username=old_user.username, # dunno if you need this, put whatever fields you want here
           password=old_user.password,
           email=old_user.email,
           first_name=old_user.first_name,
           last_name=old_user.last_name,
           is_staff=old_user.is_staff,
           is_active=old_user.is_active,
           is_superuser=old_user.is_superuser,
           # works like this, of course. And of course, i don't know if you need this
           # ckeck out django's PermissionsMixin, AbstractUser and AbstractBaseUser for all the fields
           # that the old user model had
       )
       new_user.groups.add(*old_user.groups.all())
       new_user.user_permissions.add(*old_user.user_permissions.all())
       new_user.save()
    for profile in UserProfile.objects.all():
        for key in ['crypt6_password', 'unix_username', 'unix_userid', 'locale', 'news_subscribe']:
            value = getattr(profile, key)
            setattr(profile.user, key, value)

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('supervisr_core', '0060_auto_20171018_1858'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
