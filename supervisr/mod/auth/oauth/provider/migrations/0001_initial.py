# Generated by Django 2.1.1 on 2018-09-25 10:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('supervisr_core', '0001_initial'),
        migrations.swappable_dependency(settings.OAUTH2_PROVIDER_APPLICATION_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductExtensionOAuth2',
            fields=[
                ('productextension_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervisr_core.ProductExtension')),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_core.productextension',),
        ),
    ]
