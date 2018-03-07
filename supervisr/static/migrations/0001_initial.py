# Generated by Django 2.0.2 on 2018-03-02 18:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('supervisr_core', '0007_auto_20180302_1849'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('content', models.TextField()),
                ('template', models.TextField(default='static/generic.html')),
                ('title', models.TextField()),
                ('slug', models.SlugField()),
                ('published', models.BooleanField(default=False)),
                ('listed', models.BooleanField(default=True)),
                ('views', models.BigIntegerField(default=0)),
                ('has_markdown_enabled', models.BooleanField(default=True)),
                ('has_html_enabled', models.BooleanField(default=True)),
                ('language', models.CharField(default='en', max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='FilePage',
            fields=[
                ('staticpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervisr_static.StaticPage')),
                ('path', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_static.staticpage',),
        ),
        migrations.CreateModel(
            name='ProductPage',
            fields=[
                ('staticpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervisr_static.StaticPage')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr_core.Product')),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_static.staticpage',),
        ),
        migrations.AddField(
            model_name='staticpage',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='staticpage',
            unique_together={('slug', 'language')},
        ),
    ]
