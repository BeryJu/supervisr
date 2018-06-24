# Generated by Django 2.0.2 on 2018-02-25 10:47

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr_dns', '0003_resource_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]