# Generated by Django 2.1.1 on 2018-09-25 11:12

import uuid

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import supervisr.core.fields
import supervisr.core.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('crypt6_password', models.CharField(blank=True, default='', max_length=128)),
                ('unix_username', models.CharField(default=supervisr.core.models.get_random_string, editable=False, max_length=32)),
                ('unix_userid', models.IntegerField(default=supervisr.core.models.get_userid)),
                ('locale', models.CharField(default='en-US', max_length=5)),
                ('news_subscribe', models.BooleanField(default=False)),
                ('theme', models.CharField(default='light', max_length=200)),
                ('rows_per_page', models.IntegerField(default=50)),
                ('api_key', models.UUIDField(default=uuid.uuid4)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AccountConfirmation',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('expires', models.BigIntegerField(default=supervisr.core.models.expiry_date, editable=False)),
                ('confirmed', models.BooleanField(default=False)),
                ('kind', models.IntegerField(choices=[(0, 'Sign up'), (1, 'Password Reset')], default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BaseCredential',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('glyph', models.CharField(default='envelope', max_length=200)),
                ('message', models.TextField()),
                ('current', models.BooleanField(default=True)),
                ('action_required', models.BooleanField(default=False)),
                ('action_view', models.TextField(blank=True)),
                ('action_parmas_json', models.TextField(blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('closed_date', models.DateTimeField(auto_now=True)),
                ('hidden', models.BooleanField(default=False)),
                ('send_notification', models.BooleanField(default=False)),
                ('remote_ip', models.GenericIPAddressField(default='0.0.0.0')),
                ('remote_ip_rdns', models.TextField(default='')),
                ('invoker', models.ForeignKey(default=supervisr.core.models.get_system_user, on_delete=django.db.models.deletion.CASCADE, related_name='events_invoked', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductExtension',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('extension_name', models.TextField(default='')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProviderAcquirable',
            fields=[
                ('provider_acquirable_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProviderAcquirableRelationship',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr_core.ProviderAcquirable')),
            ],
        ),
        migrations.CreateModel(
            name='ProviderAcquirableSingle',
            fields=[
                ('provider_acquirable_single_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('key', models.CharField(max_length=255)),
                ('namespace', models.CharField(max_length=255)),
                ('value', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('task_uuid', models.UUIDField()),
                ('invoker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(related_name='tasks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserAcquirable',
            fields=[
                ('user_acquirable_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserAcquirableRelationship',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='GlobalPermission',
            fields=[
            ],
            options={
                'verbose_name': 'global_permission',
                'proxy': True,
                'indexes': [],
            },
            bases=('auth.permission',),
        ),
        migrations.CreateModel(
            name='APIKeyCredential',
            fields=[
                ('basecredential_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervisr_core.BaseCredential')),
                ('api_key', supervisr.core.fields.EncryptedField()),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_core.basecredential',),
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('useracquirable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, related_name='domains', to='supervisr_core.UserAcquirable')),
                ('provideracquirablesingle_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, related_name='domains', to='supervisr_core.ProviderAcquirableSingle')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('domain_name', models.CharField(max_length=253, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'default_related_name': 'domains',
            },
            bases=('supervisr_core.provideracquirablesingle', 'supervisr_core.useracquirable', models.Model),
        ),
        migrations.CreateModel(
            name='EmptyCredential',
            fields=[
                ('basecredential_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervisr_core.BaseCredential')),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_core.basecredential',),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('useracquirable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='supervisr_core.UserAcquirable')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('slug', models.SlugField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('invite_only', models.BooleanField(default=True)),
                ('auto_add', models.BooleanField(default=False)),
                ('auto_all_add', models.BooleanField(default=False)),
                ('icon', models.ImageField(blank=True, default='', upload_to='')),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_core.useracquirable', models.Model),
        ),
        migrations.CreateModel(
            name='ProviderInstance',
            fields=[
                ('useracquirable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='supervisr_core.UserAcquirable')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('provider_path', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_core.useracquirable', models.Model),
        ),
        migrations.CreateModel(
            name='URLProductExtension',
            fields=[
                ('productextension_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervisr_core.ProductExtension')),
                ('url', models.URLField()),
                ('role', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_core.productextension',),
        ),
        migrations.CreateModel(
            name='UserPasswordCredential',
            fields=[
                ('basecredential_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervisr_core.BaseCredential')),
                ('username', models.TextField()),
                ('password', supervisr.core.fields.EncryptedField()),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_core.basecredential',),
        ),
        migrations.CreateModel(
            name='UserPasswordServerCredential',
            fields=[
                ('basecredential_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervisr_core.BaseCredential')),
                ('username', models.TextField()),
                ('password', supervisr.core.fields.EncryptedField()),
                ('server', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('supervisr_core.basecredential',),
        ),
        migrations.AddField(
            model_name='useracquirablerelationship',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr_core.UserAcquirable'),
        ),
        migrations.AddField(
            model_name='useracquirablerelationship',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='useracquirable',
            name='users',
            field=models.ManyToManyField(through='supervisr_core.UserAcquirableRelationship', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='setting',
            unique_together={('key', 'namespace')},
        ),
        migrations.AddField(
            model_name='basecredential',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='useracquirablerelationship',
            unique_together={('user', 'model')},
        ),
        migrations.AddField(
            model_name='providerinstance',
            name='credentials',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr_core.BaseCredential'),
        ),
        migrations.AddField(
            model_name='provideracquirablesingle',
            name='provider_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr_core.ProviderInstance'),
        ),
        migrations.AddField(
            model_name='provideracquirablerelationship',
            name='provider_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supervisr_core.ProviderInstance'),
        ),
        migrations.AddField(
            model_name='provideracquirable',
            name='providers',
            field=models.ManyToManyField(blank=True, through='supervisr_core.ProviderAcquirableRelationship', to='supervisr_core.ProviderInstance'),
        ),
        migrations.AddField(
            model_name='product',
            name='extensions',
            field=models.ManyToManyField(blank=True, to='supervisr_core.ProductExtension'),
        ),
        migrations.AlterUniqueTogether(
            name='basecredential',
            unique_together={('owner', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='provideracquirablerelationship',
            unique_together={('provider_instance', 'model')},
        ),
    ]
