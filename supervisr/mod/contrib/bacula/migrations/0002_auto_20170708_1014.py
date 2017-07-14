# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-08 08:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr/mod/contrib/bacula', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='basefiles',
            table='BaseFiles',
        ),
        migrations.AlterModelTable(
            name='cdimages',
            table='CDImages',
        ),
        migrations.AlterModelTable(
            name='client',
            table='Client',
        ),
        migrations.AlterModelTable(
            name='counters',
            table='Counters',
        ),
        migrations.AlterModelTable(
            name='device',
            table='Device',
        ),
        migrations.AlterModelTable(
            name='file',
            table='File',
        ),
        migrations.AlterModelTable(
            name='filename',
            table='Filename',
        ),
        migrations.AlterModelTable(
            name='fileset',
            table='FileSet',
        ),
        migrations.AlterModelTable(
            name='job',
            table='Job',
        ),
        migrations.AlterModelTable(
            name='jobhisto',
            table='JobHisto',
        ),
        migrations.AlterModelTable(
            name='jobmedia',
            table='JobMedia',
        ),
        migrations.AlterModelTable(
            name='location',
            table='Location',
        ),
        migrations.AlterModelTable(
            name='locationlog',
            table='LocationLog',
        ),
        migrations.AlterModelTable(
            name='log',
            table='Log',
        ),
        migrations.AlterModelTable(
            name='media',
            table='Media',
        ),
        migrations.AlterModelTable(
            name='mediatype',
            table='MediaType',
        ),
        migrations.AlterModelTable(
            name='path',
            table='Path',
        ),
        migrations.AlterModelTable(
            name='pathhierarchy',
            table='PathHierarchy',
        ),
        migrations.AlterModelTable(
            name='pool',
            table='Pool',
        ),
        migrations.AlterModelTable(
            name='restoreobject',
            table='RestoreObject',
        ),
        migrations.AlterModelTable(
            name='snapshot',
            table='Snapshot',
        ),
        migrations.AlterModelTable(
            name='status',
            table='Status',
        ),
        migrations.AlterModelTable(
            name='storage',
            table='Storage',
        ),
        migrations.AlterModelTable(
            name='unsavedfiles',
            table='UnsavedFiles',
        ),
        migrations.AlterModelTable(
            name='version',
            table='Version',
        ),
    ]
