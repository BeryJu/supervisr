# Generated by Django 2.1.1 on 2018-09-12 08:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervisr_core', '0005_auto_20180912_0804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='provideracquirablesingle_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='domains', serialize=False, to='supervisr_core.ProviderAcquirableSingle'),
        ),
    ]
