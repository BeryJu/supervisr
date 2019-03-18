"""supervisr core models"""
import inspect
import uuid
from difflib import get_close_matches
from importlib import import_module
from typing import Generator, List

from celery.result import AsyncResult
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.utils import OperationalError, ProgrammingError
from django.utils.translation import ugettext as _
from raven.contrib.django.raven_compat.models import client

from supervisr.core import fields
from supervisr.core.providers.base import BaseProvider
from supervisr.core.tasks import Progress

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
        try:
            return int(value)
        except ValueError:
            # Handle empty setting throwing ValueError
            return kwargs.get('default', 0)

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
    invoker = models.ForeignKey(User, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='tasks')

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


class UserAcquirable(CastableModel):
    """Base Class for Models that should have an N-M relationship with Users"""

    user_acquirable_id = models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True)
    users = models.ManyToManyField(User, through='UserAcquirableRelationship')

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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
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

class Domain(UUIDModel, ProviderAcquirableSingle, UserAcquirable, CreatedUpdatedModel):
    """Information about a Domain, which is used for other sub-apps."""

    domain_name = models.CharField(max_length=253, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.domain_name

    class Meta:

        default_related_name = 'domains'

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
