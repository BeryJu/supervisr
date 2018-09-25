"""supervisr core models"""
from __future__ import unicode_literals

import base64
import inspect
import json
import math
import random
import re
import time
import uuid
from difflib import get_close_matches
from importlib import import_module
from typing import Generator, List

from celery.result import AsyncResult
from django.conf import settings
from django.contrib.auth import models as django_auth_models
from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Max
from django.db.utils import OperationalError, ProgrammingError
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from raven.contrib.django.raven_compat.models import client

from supervisr.core import fields
from supervisr.core.decorators import database_catchall
from supervisr.core.decorators import time as time_method
from supervisr.core.providers.base import BaseProvider
from supervisr.core.tasks import Progress
from supervisr.core.utils import get_remote_ip, get_reverse_dns


def expiry_date():
    """Return the default expiry for AccountConfirmations"""
    return time.time() + 172800  # 2 days


def make_username(username):
    """Return username cut to 32 chars, also make POSIX conform"""
    return (re.sub(r'([^a-zA-Z0-9\.\s-])', '_', str(username))[:32]).lower()


def get_random_string(length=10):
    """Generate a completely random 10-char user_name (used for unix-accounts)"""
    # Generate a normal UUID, convert it to base64 and take the 10 first chars
    uid = uuid.uuid4()
    # UUID in base64 is 25 chars, we want *length* char length
    cryptogen = random.SystemRandom()
    offset = cryptogen.randint(0, 25 - length - 1)
    # Python3 changed the way we need to encode
    res = base64.b64encode(uid.bytes, altchars=b'_-')
    return res[offset:offset + length].decode("utf-8")


@database_catchall(settings.USER_PROFILE_ID_START)
def get_userid():
    """Get the next higher unix user_id, since we can't set the start for django's AutoField"""
    # Custom default to set the unix_userid since we can't have an
    # AutoField as non-primary-key. Also so we can set a custom start,
    # which is settings.USER_PROFILE_ID_START
    highest = User.objects.all().aggregate(Max('unix_userid'))['unix_userid__max']
    return highest + 1 if highest is not None else settings.USER_PROFILE_ID_START


@database_catchall(None)
def get_system_user() -> 'User':
    """Return supervisr's System User. This is created with the initial Migration,
    but might not be ID 1"""
    system_users = User.objects.filter(username=settings.SYSTEM_USER_NAME)
    if system_users.exists():
        return system_users.first()
    return None

############################
###
### Abstract Models
###
############################


class ProviderTriggerMixin(models.Model):
    """Base class for all models that trigger Provider updates"""

    @property
    def provider_instances(self) -> Generator['ProviderInstance', None, None]:
        """Return all provider instances that should be triggered"""
        raise NotImplementedError()

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Abstract base model which uses a UUID as primary key"""

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


class CastableModel(models.Model):
    """Abstract Base Model for Models using Inheritance to cast them"""

    @time_method('CastableModel.cast')
    def cast(self):
        """This method converts "self" into its correct child class."""
        for name in dir(self):
            try:
                attr = getattr(self, name)
                if isinstance(attr, self.__class__) and self.__class__ != attr.__class__:
                    return attr
            except (AttributeError, ObjectDoesNotExist, OperationalError, NotImplementedError):
                pass
        return self

    class Meta:
        abstract = True


class CreatedUpdatedModel(models.Model):
    """Base Abstract Model to save created and update"""
    created = models.DateField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(UUIDModel, AbstractUser):
    """Custom Usermodel which has a few extra fields"""

    crypt6_password = models.CharField(max_length=128, blank=True, default='')
    unix_username = models.CharField(max_length=32, default=get_random_string, editable=False)
    unix_userid = models.IntegerField(default=get_userid)
    locale = models.CharField(max_length=5, default='en-US')
    news_subscribe = models.BooleanField(default=False)
    theme = models.CharField(max_length=200, default='light')
    rows_per_page = models.IntegerField(default=50)
    api_key = models.UUIDField(default=uuid.uuid4)

    @property
    def short_name(self):
        """Get first_name if set, else username"""
        if self.first_name:
            return self.first_name
        return self.username

    def task_apply_async(self, task, *task_args, users=None, celery_kwargs=None, **task_kwargs):
        """Run task and automatically associate with user"""
        if celery_kwargs is None:
            celery_kwargs = {}
        # Add ourselves to task_kwargs
        task_kwargs['invoker'] = self.pk
        async_result = task.apply_async(args=task_args, kwargs=task_kwargs, **celery_kwargs)
        # Apply invoker to task
        setattr(async_result, 'invoker', self)
        task_obj = Task.objects.create(
            task_uuid=async_result.id,
            invoker=self,
        )
        if not users:
            users = [self]
        else:
            users = [self] + list(users)
        task_obj.users.add(*users)
        return async_result


# pylint: disable=abstract-method
class SVAnonymousUser(django_auth_models.AnonymousUser):
    """Custom Anonymous User with extra attributes"""

    locale = 'en-US'
    news_subscribe = True
    theme = 'dark'
    rows_per_page = 50
    api_key = '00000000-0000-0000-0000-000000000000'


django_auth_models.AnonymousUser = SVAnonymousUser


class GlobalPermissionManager(models.Manager):
    """GlobalPermissionManager"""

    def get_queryset(self):
        """Filter for us"""
        return super().get_queryset().filter(content_type__model='global_permission')


class GlobalPermission(Permission):
    """A global permission, not attached to a model"""

    objects = GlobalPermissionManager()

    class Meta:
        proxy = True
        verbose_name = "global_permission"

    def save(self, *args, **kwargs):
        ctype, _created = ContentType.objects.get_or_create(
            model=self._meta.verbose_name, app_label=self._meta.app_label,
        )
        self.content_type = ctype
        super().save(*args, **kwargs)


class Setting(UUIDModel, CreatedUpdatedModel):
    """Save key-value settings to db"""

    key = models.CharField(max_length=255)
    namespace = models.CharField(max_length=255)
    value = models.TextField(null=True, blank=True)

    __ALLOWED_NAMESPACES = []

    @staticmethod
    def _init_allowed():
        from supervisr.core.utils import get_apps
        Setting.__ALLOWED_NAMESPACES = [x.name for x in get_apps(exclude=[])]

    @property
    def value_bool(self) -> bool:
        """Return value converted to boolean

        Returns:
            True if value converted to lowercase equals 'true'. Otherwise False.
        """
        if not isinstance(self.value, str):
            self.value = str(self.value)
        return self.value.lower() == 'true'

    @property
    def value_int(self, default: int = 0) -> int:
        """Return value converted to integer

        Returns:
            True if value converted to lowercase equals 'true'. Otherwise False.
        """
        try:
            return int(self.value)
        except ValueError:
            return default

    def __str__(self):
        return "%s/%s" % (self.namespace, self.key)

    @staticmethod
    def get(key: str, namespace='', default='', inspect_offset=1) -> str:
        """Get value, when Setting doesn't exist, it's created with default

        Args:
            key: Key for which to look
            namespace: Optional. Namespace in which to look. By Default this is determined by
                looking up into the stack and extracting the module.
            default: This value is returned if the namespace is invalid / not allowed. If no
                Setting with the specified namespace/key combo is found, one is created with
                default as value.
            inspect_offset: The offset by which the stack should be looked up. Defaults to 1.
                This can be used if you wrap this function (like `Setting.get_bool`) and need
                to increase the offset to 2.

        Returns:
            The data currently saved if the Setting exists. Otherwise `default` is returned.
        """
        if not Setting.__ALLOWED_NAMESPACES:
            Setting._init_allowed()
        if namespace == '':
            namespace = inspect.getmodule(inspect.stack()[inspect_offset][0]).__name__
        for name in Setting.__ALLOWED_NAMESPACES:
            if namespace.startswith(name):
                namespace = name
        namespace_matches = get_close_matches(namespace, Setting.__ALLOWED_NAMESPACES)
        if not namespace_matches:
            return default
        namespace = namespace_matches[0]
        try:
            setting = Setting.objects.get_or_create(
                key=key,
                namespace=namespace,
                defaults={'value': default})[0]
            return setting.value
        except (OperationalError, ProgrammingError):
            return default

    @staticmethod
    def get_bool(*args, **kwargs) -> bool:
        """Return value cast to boolean

        This is wrapper around `Setting.get`, which returns a boolean.

        Returns:
            True if the Setting's value in lowercase is equal to 'true'. Otherwise False.
        """
        value = Setting.get(*args, inspect_offset=2, **kwargs)
        if not isinstance(value, str):
            value = str(value)
        return str(value).lower() == 'true'

    @staticmethod
    def get_int(*args, **kwargs) -> int:
        """Return value cast to int

        This is wrapper around `Setting.get`, which returns a boolean.

        Returns:
            True if the Setting's value in lowercase is equal to 'true'. Otherwise False.
        """
        value = Setting.get(*args, inspect_offset=2, **kwargs)
        if not isinstance(value, str):
            value = str(value)
        return int(value)

    @staticmethod
    def set(key: str, value: str, namespace='', inspect_offset=1) -> bool:
        """Set value, when Setting doesn't exist, it's created with value

        Args:
            key: The key with which the setting should be created
            value: Value to write to the Setting.
            namespace: Namespace under which this Setting should be saved. By Default this is
                determined by looking up into the stack and extracting the module.
            inspect_offset: The offset by which the stack should be looked up. Defaults to 1.
                This can be used if you wrap this function (like `Setting.get_bool`) and need
                to increase the offset to 2.

        Returns:
            True if saving the Setting succeeded, otherwise False.
        """
        if not Setting.__ALLOWED_NAMESPACES:
            Setting._init_allowed()
        if namespace == '':
            namespace = inspect.getmodule(
                inspect.stack()[inspect_offset][0]).__name__
        for name in Setting.__ALLOWED_NAMESPACES:
            if namespace.startswith(name):
                namespace = name
        namespace = get_close_matches(namespace, Setting.__ALLOWED_NAMESPACES)[0]
        try:
            setting, created = Setting.objects.get_or_create(
                key=key,
                namespace=namespace,
                defaults={'value': value})
            if created is False:
                setting.value = value
                setting.save()
            return True
        except OperationalError:
            return False

    class Meta:

        unique_together = (('key', 'namespace'), )


class Task(UUIDModel, CreatedUpdatedModel):
    """Model to associate users with tasks"""

    task_uuid = models.UUIDField()
    invoker = models.ForeignKey('User', on_delete=models.CASCADE)
    users = models.ManyToManyField('User', related_name='tasks')

    @property
    def result(self):
        """Get task result"""
        return AsyncResult(self.task_uuid)

    @property
    def progress(self):
        """Get Progress instance for this task"""
        return Progress(self.task_uuid).get_info()

    def __str__(self):
        return "Task %s (invoker: %s)" % (self.task_uuid, self.invoker)


class AccountConfirmation(UUIDModel, CreatedUpdatedModel):
    """Save information about actions that need to be confirmed"""

    KIND_SIGN_UP = 0
    KIND_PASSWORD_RESET = 1
    ACCOUNT_CONFIRMATION_KIND = (
        (KIND_SIGN_UP, _('Sign up')),
        (KIND_PASSWORD_RESET, _('Password Reset')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expires = models.BigIntegerField(default=expiry_date, editable=False)
    confirmed = models.BooleanField(default=False)
    kind = models.IntegerField(choices=ACCOUNT_CONFIRMATION_KIND, default=0)

    @property
    def is_expired(self):
        """Returns whether or not the confirmation is expired or not"""
        return self.expires < time.time()

    def __str__(self):
        return "AccountConfirmation %s, expired: %r" % \
            (self.user.email, self.is_expired)


class ProductExtension(UUIDModel, CreatedUpdatedModel, CastableModel):
    """This class can be used by extension to associate Data with a Product"""

    extension_name = models.TextField(default='')
    form = 'supervisr.core.forms.products.ProductExtensionForm'

    def __str__(self):
        return "ProductExtension %s" % self.extension_name


class URLProductExtension(ProductExtension):
    """Attach a URL to a product. URLProductExtensions with role set to 'primary' is shown
    in the webinterface"""

    url = models.URLField()
    role = models.TextField()

    def __str__(self):
        return "URLProductExtension '%s' role: %s" % (self.url, self.role)


class UserAcquirable(CastableModel):
    """Base Class for Models that should have an N-M relationship with Users"""

    user_acquirable_id = models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True)
    users = models.ManyToManyField('User', through='UserAcquirableRelationship')

    def has_user(self, user: User) -> bool:
        """Check if user has acquired this instance"""
        return user in self.users.all()

    def copy_user_relationships_to(self, target: 'UserAcquirable'):
        """Copy UserAcquirableRelationship associated with `self` and copy them to `to`"""
        for user_id in self.useracquirablerelationship_set \
                .values_list('user', flat=True).distinct():
            UserAcquirableRelationship.objects.create(
                model=target,
                user=User.objects.get(pk=user_id)
            )


class UserAcquirableRelationship(UUIDModel):
    """Relationship between User and any Class subclassing UserAcquirable"""

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    model = models.ForeignKey('UserAcquirable', on_delete=models.CASCADE)

    def __str__(self):
        return "User '%s' <=> UserAcquirable '%s'" % (self.user, self.model.cast())

    class Meta:
        unique_together = (('user', 'model'),)


class ProviderAcquirable(ProviderTriggerMixin, CastableModel):
    """Base Class for Models that should have an N-M relationship with ProviderInstance"""

    provider_acquirable_id = models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True)
    providers = models.ManyToManyField('ProviderInstance',
                                       through='ProviderAcquirableRelationship', blank=True)

    @property
    def provider_instances(self) -> Generator['ProviderInstance', None, None]:
        """Return all provider instances that should be triggered"""
        return self.providers.all().iterator()

    def update_provider_m2m(self, provider_list: List['ProviderInstance']):
        """Update m2m relationship to providers from form list"""
        for provider_instance in provider_list:
            if not ProviderAcquirableRelationship.objects.filter(
                    provider_instance=provider_instance,
                    model=self).exists():
                ProviderAcquirableRelationship.objects.create(
                    provider_instance=provider_instance,
                    model=self
                )
        for relationship in ProviderAcquirableRelationship.objects.filter(model=self):
            if relationship.provider_instance not in provider_list:
                relationship.delete()


class ProviderAcquirableSingle(ProviderTriggerMixin, CastableModel):
    """Base Class for Models that should have an N-1 relationship with ProviderInstance"""

    provider_acquirable_single_id = models.UUIDField(
        editable=False, default=uuid.uuid4, primary_key=True)
    provider_instance = models.ForeignKey('ProviderInstance', on_delete=models.CASCADE)

    @property
    def provider_instances(self) -> Generator['ProviderInstance', None, None]:
        """Return all provider instances that should be triggered"""
        yield self.provider_instance


class ProviderAcquirableRelationship(UUIDModel):
    """Relationship between ProviderInstance and any Class subclassing ProviderAcquirable"""

    provider_instance = models.ForeignKey('ProviderInstance', on_delete=models.CASCADE)
    model = models.ForeignKey('ProviderAcquirable', on_delete=models.CASCADE)

    def __str__(self):
        return "ProviderAcquirable '%s' <=> ProviderInstance '%s'" \
            % (self.model.cast(), self.provider_instance)

    class Meta:

        unique_together = (('provider_instance', 'model'),)


class Product(UUIDModel, CreatedUpdatedModel, UserAcquirable, CastableModel):
    """Information about the Main Product itself. This instances of this classes
    are assumed to be managed services."""

    name = models.TextField()
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    invite_only = models.BooleanField(default=True)
    auto_add = models.BooleanField(default=False)
    auto_all_add = models.BooleanField(default=False)
    extensions = models.ManyToManyField(ProductExtension, blank=True)
    icon = models.ImageField(blank=True, default='')

    def __str__(self):
        return "%s '%s'" % (self.cast().__class__.__name__, self.name)

    def primary_url(self):
        """Return URL if Product has a URL that should
        be shown in the app launcher, otherwise None"""
        urls = URLProductExtension.objects.filter(product__in=[self], role='primary')
        if not urls.exists():
            return False
        return urls.first().url

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # Auto generate slug
        self.slug = slugify(self.name)

        super().save(force_insert, force_update, using, update_fields)
        if self.auto_all_add is True:
            # Since there is no better way to do the query other way roundd
            # We have to do it like this
            rels = list(UserAcquirableRelationship.objects.filter(model=self))
            rels_userlist = []
            users = list(User.objects.all())
            for rel in rels:
                rels_userlist.append(rel.user)
            missing_users = set(rels_userlist).symmetric_difference(set(users))
            for missing_user in missing_users:
                UserAcquirableRelationship.objects.create(
                    user=missing_user,
                    model=self)


class Domain(UUIDModel, ProviderAcquirableSingle, UserAcquirable, CreatedUpdatedModel):
    """Information about a Domain, which is used for other sub-apps."""

    domain_name = models.CharField(max_length=253, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.domain_name

    class Meta:

        default_related_name = 'domains'


class Event(CreatedUpdatedModel):
    """Store information about important Event's for auditing, like signing up, changing/resetting
    your password or gaining access to a new Product"""

    EVENT_IMPORTANCE_URGENT = 40
    EVENT_IMPORTANCE_IMPORTANT = 30
    EVENT_IMPORTANCE_MEDIUM = 20
    EVENT_IMPORTANCE_NOTICE = 10
    EVENT_IMPORTANCE_INFORMATION = 0
    EVENT_IMPORTANCE = (
        (EVENT_IMPORTANCE_URGENT, _('Urgent')),
        (EVENT_IMPORTANCE_IMPORTANT, _('Important')),
        (EVENT_IMPORTANCE_MEDIUM, _('Medium')),
        (EVENT_IMPORTANCE_NOTICE, _('Notice')),
        (EVENT_IMPORTANCE_INFORMATION, _('Information'))
    )

    # This model uses a classic AutoField primary key for performance reasons
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    glyph = models.CharField(max_length=200, default='envelope')
    message = models.TextField()
    current = models.BooleanField(default=True)
    action_required = models.BooleanField(default=False)
    action_view = models.TextField(blank=True)
    action_parmas_json = models.TextField(blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    closed_date = models.DateTimeField(auto_now=True)
    invoker = models.ForeignKey(User, default=get_system_user,
                                related_name='events_invoked',
                                on_delete=models.CASCADE)
    hidden = models.BooleanField(default=False)
    send_notification = models.BooleanField(default=False)
    remote_ip = models.GenericIPAddressField(default='0.0.0.0') # nosec
    remote_ip_rdns = models.TextField(default='')

    @property
    def action_parmas(self):
        """Return action's params as dict"""
        return json.loads(self.action_parmas_json)

    @action_parmas.setter
    def action_params(self, value):
        """Set action's params from a dict and saves it as json"""
        self.action_parmas_json = json.dumps(value)

    @property
    def get_url(self):
        """Returns relative url for action with params"""
        return reverse(self.action_view, kwargs=self.action_parmas)

    @property
    def create_timestamp(self):
        """Get create date as timestmap"""
        return self.create_date.timestamp()

    @property
    def get_localized_age(self):
        """Return age as a localized String"""
        now = timezone.now()
        diff = now - self.create_date
        hours = int(diff.seconds / 3600)
        minutes = int(math.ceil(diff.seconds / 60))
        if diff.days > 0:
            return _("%(days)d day(s) ago" % {'days': diff.days})
        if hours > 0:
            return _("%(hours)d hour(s) ago" % {'hours': hours})
        return _("%(minutes)d minute(s) ago" % {'minutes': minutes})

    @staticmethod
    def create(**kwargs):
        """Create an event and set reverse DNS and remote IP"""
        if 'request' in kwargs:
            request = kwargs.get('request')
            kwargs['remote_ip'] = get_remote_ip(request)
            kwargs['remote_ip_rdns'] = get_reverse_dns(kwargs.get('remote_ip'))
            del kwargs['request']
        return Event.objects.create(**kwargs)

    def __str__(self):
        return "Event '%s' '%s'" % (self.user.username, self.message)


class BaseCredential(UUIDModel, CreatedUpdatedModel, CastableModel):
    """Basic set of credentials"""

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    form = ''  # form class which is used for setup

    @staticmethod
    def all_types():
        """Return all subclasses"""
        return BaseCredential.__subclasses__()

    @staticmethod
    def type():
        """Return type"""
        return 'BaseCredential'

    def __str__(self):
        return "%s %s" % (self.cast().type(), self.name)

    class Meta:
        unique_together = (('owner', 'name'),)


class EmptyCredential(BaseCredential):
    """Empty Credential"""

    form = 'supervisr.core.forms.providers.EmptyCredentialForm'

    @staticmethod
    def type():
        """Return type"""
        return _('Empty Credential')


class APIKeyCredential(BaseCredential):
    """Credential which work with an API Key"""

    api_key = fields.EncryptedField()
    form = 'supervisr.core.forms.providers.NewCredentialAPIForm'

    @staticmethod
    def type():
        """Return type"""
        return _('API Key')


class UserPasswordCredential(BaseCredential):
    """Credentials which need a Username and Password"""

    username = models.TextField()
    password = fields.EncryptedField()
    form = 'supervisr.core.forms.providers.NewCredentialUserPasswordForm'

    @staticmethod
    def type():
        """Return type"""
        return _('Username and Password')


class UserPasswordServerCredential(BaseCredential):
    """UserPasswordCredential which also holds a server"""

    username = models.TextField()
    password = fields.EncryptedField()
    server = models.CharField(max_length=255)
    form = 'supervisr.core.forms.providers.NewCredentialUserPasswordServerForm'

    @staticmethod
    def type():
        """Return type"""
        return _("Username, Password and Server")


class ProviderInstance(UUIDModel, CreatedUpdatedModel, UserAcquirable):
    """Basic Provider Instance"""

    name = models.TextField()
    provider_path = models.TextField()
    credentials = models.ForeignKey('BaseCredential', on_delete=models.CASCADE)
    _class = None

    @property
    def provider(self) -> BaseProvider:
        """Return instance of provider saved"""
        try:
            if not self._class:
                path_parts = self.provider_path.split('.')
                module = import_module('.'.join(path_parts[:-1]))
                self._class = getattr(module, path_parts[-1])
            return self._class(credentials=self.credentials)
        # We do a broad catch here since the mainly runs in the main thread
        # and we dont want to disrupt anything if a provider errors out
        except Exception: # pylint: disable=broad-except
            client.captureException()
        return None

    def __str__(self):
        return self.name
