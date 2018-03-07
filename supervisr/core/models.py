"""
Core Modules for supervisr
"""
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

import django.contrib.auth.models as django_auth_models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import AppRegistryNotReady, ObjectDoesNotExist
from django.db import models
from django.db.models import Max, options
from django.db.models.signals import post_save, pre_delete
from django.db.utils import InternalError, OperationalError, ProgrammingError
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _

from supervisr.core import fields
from supervisr.core.decorators import time as time_method
from supervisr.core.providers.base import BaseProvider
from supervisr.core.signals import (SIG_DOMAIN_CREATED, SIG_SETTING_UPDATE,
                                    SIG_USER_ACQUIRABLE_RELATIONSHIP_CREATED,
                                    SIG_USER_ACQUIRABLE_RELATIONSHIP_DELETED,
                                    SIG_USER_POST_SIGN_UP)
from supervisr.core.utils import get_remote_ip, get_reverse_dns

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('sv_search_url', 'sv_search_fields',)

def expiry_date():
    """
    Return the default expiry for AccountConfirmations
    """
    return time.time() + 172800 # 2 days

def make_username(username):
    """
    Return username cut to 32 chars, also make POSIX conform
    """
    return (re.sub(r'([^a-zA-Z0-9\.\s-])', '_', str(username))[:32]).lower()

def get_random_string(length=10):
    """
    Generate a completely random 10-char user_name (used for unix-accounts)
    """
    # Generate a normal UUID, convert it to base64 and take the 10 first chars
    uid = uuid.uuid4()
    # UUID in base64 is 25 chars, we want *length* char length
    offset = random.randint(0, 25 - length - 1)
    # Python3 changed the way we need to encode
    res = base64.b64encode(uid.bytes, altchars=b'_-')
    return res[offset:offset+length].decode("utf-8")

def get_userid():
    """
    Get the next higher unix user_id, since we can't set the start for django's AutoField
    """
    # Custom default to set the unix_userid since we can't have an
    # AutoField as non-primary-key. Also so we can set a custom start,
    # which is settings.USER_PROFILE_ID_START
    try:
        highest = User.objects.all().aggregate(Max('unix_userid'))['unix_userid__max']
        return highest + 1 if highest is not None else settings.USER_PROFILE_ID_START
    except (AppRegistryNotReady, ObjectDoesNotExist,
            OperationalError, InternalError, ProgrammingError):
        # Handle Postgres transaction revert
        if 'postgresql' in settings.DATABASES['default']['ENGINE']:
            from django.db import connection
            # pylint: disable=protected-access
            connection._rollback()
        return settings.USER_PROFILE_ID_START

def get_system_user():
    """
    Return supervisr's System User PK. This is created with the initial Migration,
    but might not be ID 1
    """
    system_users = User.objects.filter(username=settings.SYSTEM_USER_NAME)
    if system_users.exists():
        return system_users.first().id
    return 1 # Django starts AutoField's with 1 not 0

class CastableModel(models.Model):
    """
    Base Model for Models using Inheritance to cast them
    """

    @time_method('CastableModel.cast')
    def cast(self):
        """
        This method converts "self" into its correct child class.
        """
        for name in dir(self):
            try:
                attr = getattr(self, name)
                if isinstance(attr, self.__class__):
                    return attr
            except (AttributeError, ObjectDoesNotExist, OperationalError):
                pass
        return self

    class Meta:
        abstract = True

class CreatedUpdatedModel(models.Model):
    """
    Base Abstract Model to save created and update
    """
    created = models.DateField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class User(AbstractUser):
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

# pylint: disable=abstract-method
class SVAnonymousUser(django_auth_models.AnonymousUser):
    """Custom Anonymous User with extra attributes"""

    locale = 'en-US'
    news_subscribe = True
    theme = 'light'
    rows_per_page = 50
    api_key = '00000000-0000-0000-0000-000000000000'

django_auth_models.AnonymousUser = SVAnonymousUser

# pylint: disable=too-few-public-methods
class GlobalPermissionManager(models.Manager):
    """GlobalPermissionManager"""

    def get_queryset(self):
        """Filter for us"""
        return super(GlobalPermissionManager, self).\
            get_queryset().filter(content_type__model='global_permission')

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
        super(GlobalPermission, self).save(*args, **kwargs)

class Setting(CreatedUpdatedModel):
    """
    Save key-value settings to db
    """
    setting_id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=255)
    namespace = models.CharField(max_length=255)
    value = models.TextField(null=True, blank=True)

    _ALLOWED_NAMESPACES = []

    @staticmethod
    def _init_allowed():
        from supervisr.core.utils import get_apps
        Setting._ALLOWED_NAMESPACES = [x.name for x in get_apps(exclude=[])]

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
        return "Setting %s/%s" % (self.namespace, self.key)

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
        if not Setting._ALLOWED_NAMESPACES:
            Setting._init_allowed()
        if namespace == '':
            namespace = inspect.getmodule(inspect.stack()[inspect_offset][0]).__name__
        for name in Setting._ALLOWED_NAMESPACES:
            if namespace.startswith(name):
                namespace = name
        namespace_matches = get_close_matches(namespace, Setting._ALLOWED_NAMESPACES)
        if len(namespace_matches) < 1:
            return default
        else:
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
        if not Setting._ALLOWED_NAMESPACES:
            Setting._init_allowed()
        if namespace == '':
            namespace = inspect.getmodule(
                inspect.stack()[inspect_offset][0]).__name__
        for name in Setting._ALLOWED_NAMESPACES:
            if namespace.startswith(name):
                namespace = name
        namespace = get_close_matches(namespace, Setting._ALLOWED_NAMESPACES)[0]
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

    def save(self, *args, **kwargs):
        res = super(Setting, self).save(*args, **kwargs)
        SIG_SETTING_UPDATE.send(sender=self, setting=self)
        return res

    class Meta:

        unique_together = (('key', 'namespace'), )

class AccountConfirmation(CreatedUpdatedModel):
    """
    Save information about actions that need to be confirmed
    """

    KIND_SIGN_UP = 0
    KIND_PASSWORD_RESET = 1
    ACCOUNT_CONFIRMATION_KIND = (
        (KIND_SIGN_UP, _('Sign up')),
        (KIND_PASSWORD_RESET, _('Password Reset')),
    )

    account_confirmation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expires = models.BigIntegerField(default=expiry_date, editable=False)
    confirmed = models.BooleanField(default=False)
    kind = models.IntegerField(choices=ACCOUNT_CONFIRMATION_KIND, default=0)

    @property
    def is_expired(self):
        """
        Returns whether or not the confirmation is expired or not
        """
        return self.expires < time.time()

    def __str__(self):
        return "AccountConfirmation %s, expired: %r" % \
            (self.user.email, self.is_expired)

@receiver(pre_delete)
# pylint: disable=unused-argument
def relationship_pre_delete(sender, instance, **kwargs):
    """Send signal when relationship is deleted"""
    if sender == UserAcquirableRelationship:
        # Send signal to we are going to be deleted
        SIG_USER_ACQUIRABLE_RELATIONSHIP_DELETED.send(
            sender=UserAcquirableRelationship,
            relationship=instance)

class ProductExtension(CreatedUpdatedModel, CastableModel):
    """
    This class can be used by extension to associate Data with a Product
    """

    product_extension_id = models.AutoField(primary_key=True)
    extension_name = models.TextField(default='')

    def __str__(self):
        return "ProductExtension %s" % self.extension_name

class StagedProviderChange(CreatedUpdatedModel):
    """Store information about a staged Provider change"""

    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'

    ACTIONS = (
        (ACTION_CREATE, _('Create')),
        (ACTION_UPDATE, _('Update')),
        (ACTION_DELETE, _('Delete'))
    )

    provider_instance = models.ForeignKey('ProviderInstance', on_delete=models.CASCADE)
    model_path = models.TextField(help_text=_('Django-style path, <app_label>.<model_name>'))
    action = models.CharField(max_length=20, choices=ACTIONS)
    body = models.TextField(help_text=_('This data is directly passed to the marshall as arg.'))

    def __str__(self):
        return "StagedProviderChange %s %s" % (self.action, self.model_path)

class UserAcquirable(CastableModel):
    """Base Class for Models that should have an N-M relationship with Users"""

    user_acquirable_id = models.AutoField(primary_key=True)
    users = models.ManyToManyField('User', through='UserAcquirableRelationship')

    def copy_user_relationships_to(self, target: 'UserAcquirable'):
        """Copy UserAcquirableRelationship associated with `self` and copy them to `to`"""
        for user_id in self.useracquirablerelationship_set \
          .values_list('user', flat=True).distinct():
            UserAcquirableRelationship.objects.create(
                model=target,
                user=User.objects.get(pk=user_id)
            )

class UserAcquirableRelationship(models.Model):
    """Relationship between User and any Class subclassing UserAcquirable"""

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    model = models.ForeignKey('UserAcquirable', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.pk is None:
            # Trigger event that we were saved
            SIG_USER_ACQUIRABLE_RELATIONSHIP_CREATED.send(
                sender=UserAcquirableRelationship,
                relationship=self)
        super(UserAcquirableRelationship, self).save(*args, **kwargs)

    def __str__(self):
        return "User '%s' <=> UserAcquirable '%s'" % (self.user, self.model.cast())

    class Meta:

        unique_together = (('user', 'model'),)

class ProviderAcquirable(CastableModel):
    """Base Class for Models that should have an N-M relationship with ProviderInstance"""

    provider_acquirable_id = models.AutoField(primary_key=True)
    providers = models.ManyToManyField('ProviderInstance',
                                       through='ProviderAcquirableRelationship', blank=True)

class ProviderAcquirableSingle(CastableModel):
    """Base Class for Models that should have an N-1 relationship with ProviderInstance"""

    provider_acquirable_Single_id = models.AutoField(primary_key=True)
    provider_instance = models.ForeignKey('ProviderInstance', on_delete=models.CASCADE)

class ProviderAcquirableRelationship(models.Model):
    """Relationship between ProviderInstance and any Class subclassing ProviderAcquirable"""

    provider_instance = models.ForeignKey('ProviderInstance', on_delete=models.CASCADE)
    model = models.ForeignKey('ProviderAcquirable', on_delete=models.CASCADE)

    def __str__(self):
        return "ProviderAcquirable '%s' <=> ProviderInstance '%s'" \
            % (self.model.cast(), self.provider_instance)

    class Meta:

        unique_together = (('provider_instance', 'model'),)

class Product(CreatedUpdatedModel, UserAcquirable, CastableModel):
    """
    Information about the Main Product itself. This instances of this classes
    are assumed to be managed services.
    """
    product_id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.TextField()
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(decimal_places=3, max_digits=65, default=0.00)
    invite_only = models.BooleanField(default=True)
    auto_add = models.BooleanField(default=False)
    auto_all_add = models.BooleanField(default=False)
    revision = models.IntegerField(default=1)
    managed = models.BooleanField(default=True)
    management_url = models.URLField(max_length=1000, blank=True, null=True)
    extensions = models.ManyToManyField(ProductExtension, blank=True)
    icon = models.ImageField(blank=True, default='')

    def __str__(self):
        return "%s '%s'" % (self.cast().__class__.__name__, self.name)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # Auto generate slug
        self.slug = slugify(self.name)

        super(Product, self).save(force_insert, force_update, using, update_fields)
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

class Domain(UserAcquirable, ProviderAcquirableSingle, CreatedUpdatedModel):
    """
    Information about a Domain, which is used for other sub-apps.
    This is also used for sub domains, hence the is_sub.
    """
    domain_name = models.CharField(max_length=253, unique=True)
    is_sub = models.BooleanField(default=False)

    def __str__(self):
        return self.domain_name

    class Meta:

        default_related_name = 'domains'
        sv_search_fields = ['domain_name', 'provider_instance__name']

class Event(CreatedUpdatedModel):
    """
    Store information about important Event's for auditing, like signing up, changing/resetting
    your password or gaining access to a new Product
    """

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

    event_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    remote_ip = models.GenericIPAddressField(default='0.0.0.0')
    remote_ip_rdns = models.TextField(default='')

    @property
    def action_parmas(self):
        """
        Return action's params as dict
        """
        return json.loads(self.action_parmas_json)

    @action_parmas.setter
    def action_params(self, value):
        """
        Set action's params from a dict and saves it as json
        """
        self.action_parmas_json = json.dumps(value)

    @property
    def get_url(self):
        """
        Returns relative url for action with params
        """
        return reverse(self.action_view, kwargs=self.action_parmas)

    @property
    def create_timestamp(self):
        """Get create date as timestmap"""
        return self.create_date.timestamp()

    @property
    def get_localized_age(self):
        """
        Return age as a localized String
        """
        now = timezone.now()
        diff = now - self.create_date
        hours = int(diff.seconds / 3600)
        minutes = int(math.ceil(diff.seconds / 60))
        if diff.days > 0:
            return _("%(days)d day(s) ago" % {'days': diff.days})
        elif hours > 0:
            return _("%(hours)d hour(s) ago" % {'hours': hours})
        return _("%(minutes)d minute(s) ago" % {'minutes': minutes})

    @staticmethod
    def create(**kwargs):
        """
        Create an event and set reverse DNS and remote IP
        """
        if 'request' in kwargs:
            request = kwargs.get('request')
            kwargs['remote_ip'] = get_remote_ip(request)
            kwargs['remote_ip_rdns'] = get_reverse_dns(kwargs.get('remote_ip'))
            del kwargs['request']
        return Event.objects.create(**kwargs)

    def __str__(self):
        return "Event '%s' '%s'" % (self.user.username, self.message)

class BaseCredential(CreatedUpdatedModel, CastableModel):
    """Basic set of credentials"""
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    form = '' # form class which is used for setup

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
    """
    Credentials which need a Username and Password
    """
    username = models.TextField()
    password = fields.EncryptedField()
    form = 'supervisr.core.forms.providers.NewCredentialUserPasswordForm'

    @staticmethod
    def type():
        """
        Return type
        """
        return _('Username and Password')

class UserPasswordServerCredential(BaseCredential):
    """
    UserPasswordCredential which also holds a server
    """
    username = models.TextField()
    password = fields.EncryptedField()
    server = models.CharField(max_length=255)
    form = 'supervisr.core.forms.providers.NewCredentialUserPasswordServerForm'

    @staticmethod
    def type():
        """
        Return type
        """
        return _("Username, Password and Server")


class ProviderInstance(CreatedUpdatedModel, UserAcquirable):
    """Basic Provider Instance"""

    name = models.TextField()
    uuid = models.UUIDField(default=uuid.uuid4)
    provider_path = models.TextField()
    credentials = models.ForeignKey('BaseCredential', on_delete=models.CASCADE)
    _class = None

    @property
    def provider(self) -> BaseProvider:
        """Return instance of provider saved"""
        if not self._class:
            path_parts = self.provider_path.split('.')
            module = import_module('.'.join(path_parts[:-1]))
            self._class = getattr(module, path_parts[-1])
        return self._class(credentials=self.credentials)

    def __str__(self):
        return self.name

@receiver(SIG_USER_POST_SIGN_UP)
# pylint: disable=unused-argument
def product_handle_post_signup(sender, signal, user, **kwargs):
    """
    Auto-associates Product with new users. We have a separate function for
    this since we use the default Django User Model.
    """
    to_add = Product.objects.filter(auto_add=True)
    for product in to_add:
        UserAcquirableRelationship.objects.create(
            user=user,
            model=product)

@receiver(post_save, sender=Domain)
# pylint: disable=unused-argument
def send_domain_create(sender, signal, instance, created, **kwargs):
    """Send Domain creation signal"""
    if created:
        SIG_DOMAIN_CREATED.send(
            sender=Domain,
            domain=instance)
