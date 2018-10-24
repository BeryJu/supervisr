"""Supervisr core app config"""

import importlib
import logging
import os
import uuid

import pkg_resources
from django.apps import AppConfig
from django.conf import settings
from django.core.cache import cache
from django.db.utils import InternalError, OperationalError, ProgrammingError
from pip._internal.req import parse_requirements

LOGGER = logging.getLogger(__name__)


class SupervisrAppConfig(AppConfig):
    """Base AppConfig Class that logs when it's loaded"""

    init_modules = ['signals', 'models', 'search', 'api.serializers']
    admin_url_name = 'admin-module_default'
    view_user_settings = None
    navbar_enabled = lambda self, request: False
    title_modifier = lambda self, request: self.verbose_name.title()

    def __init__(self, *args, **kwargs):
        """Set app Label based on full name"""
        self.label = self.name.replace('.', '_')
        super().__init__(*args, **kwargs)

    def ready(self):
        # self.check_requirements()
        self.__load_init()
        self.merge_settings()
        self.run_bootstrap()
        super().ready()

    def clear_cache(self):
        """Clear cache on startup"""
        cache.clear()
        LOGGER.debug("Successfully cleared Cache")

    def run_bootstrap(self):
        """Run and apply all boostrappers"""
        try:
            bootstrappers = self.bootstrap()
            for bootstrapper in bootstrappers:
                bootstrapper.apply(self)
        except (OperationalError, ProgrammingError, InternalError):
            pass

    def bootstrap(self):
        """Bootstrap Settings or Permissions"""
        return []

    def __load_init(self):
        """Load initial modules for decorators"""
        LOGGER.debug("Loaded %s", self.name)
        for module in self.init_modules:
            try:
                if importlib.util.find_spec("%s.%s" % (self.name, module)) is not None:
                    importlib.import_module("%s.%s" % (self.name, module))
                    LOGGER.debug("Loaded %s.%s", self.name, module)
            except Exception as exc:  # pylint: disable=broad-except
                # If module is declared in BaseClass it's optional, so we don't care about failure
                if module in SupervisrAppConfig.init_modules:
                    LOGGER.warning(exc)
                # Otherwise raise error since module has been declared explicitly
                else:
                    raise exc

    def check_requirements(self):
        """Check requirements(-dev) and see if everything is installed"""

        def _check_file(self, path):
            # Basedir
            basedir = (os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.realpath(__file__)))))
            # Path to the this module
            subdir = os.sep.join(self.__module__.split('.')[:-1])
            # Complete path to *path
            path = os.path.join(basedir, subdir, path)

            if not os.path.isfile(path):
                # Path is not a file, assume this module has no requirements
                return False

            # Read file and parse all lines
            install_reqs = parse_requirements(path, session='hack')

            pkg_resources.require([str(x.requirement) for x in install_reqs])
            return True

        _check_file(self, 'requirements.txt')
        if settings.DEBUG:
            _check_file(self, 'requirements-dev.txt')

    def merge_settings(self, overwrite=False):
        """Load settings file and add/overwrite.

        A similar thing is also done in settings.py itself, so you can modify INSTALLED_APPS
        and such."""
        blacklist = ['INSTALLED_APPS', 'MIDDLEWARE', 'SECRET_KEY']
        try:
            counter = 0
            sub_settings = importlib.import_module("%s.settings" % self.name)
            for key in dir(sub_settings):
                if not key.startswith('__') and not key.endswith('__') and key.isupper():
                    # Only overwrite if set
                    if overwrite is True or \
                            hasattr(settings, key) is False and \
                            key not in blacklist:
                        value = getattr(sub_settings, key)
                        setattr(settings, key, value)
                        counter += 1
            if counter > 0:
                LOGGER.debug("Overwrote %s settings for %s", counter, self.name)
        except ImportError:
            pass  # ignore non-existant modules


class Bootstrapper:
    """Class to help with ensuring certain Model instances exist on startup"""

    rows = []

    def __init__(self):
        self.rows = []

    def add(self, **kwargs):
        """Add a row that should be applied"""
        self.rows.append(kwargs)

    def apply(self, invoker):
        """Apply rows to database. This method must be overwritten by subclasses"""
        raise NotImplementedError()


class SettingBootstrapper(Bootstrapper):
    """Bootstrapper to create Settings"""

    def apply(self, invoker):
        from supervisr.core.models import Setting
        namespace = '.'.join(invoker.__module__.split('.')[:-1])
        for row in self.rows:
            Setting.objects.get_or_create(
                key=row.get('key'),
                namespace=namespace,
                defaults={'value': row.get('value')})


class PermissionBootstrapper(Bootstrapper):
    """Bootstrapper to create Permissions"""

    def apply(self, invoker):
        from supervisr.core.models import GlobalPermission
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(GlobalPermission)
        for row in self.rows:
            row['content_type'] = content_type
            Permission.objects.get_or_create(**row)


class SupervisrCoreConfig(SupervisrAppConfig):
    """Supervisr core app config"""

    name = 'supervisr.core'
    label = 'supervisr_core'
    init_modules = [
        'logger',
        'signals',
        'events',
        'mailer',
        'models',
        'providers.base',
        'providers.domain',
        'providers.tasks',
        'search',
        'api.serializers.base',
        'api.serializers.core',
        'utils.statistics',
    ]
    navbar_title = 'Core'
    verbose_name = 'Supervisr Core'

    def ready(self):
        LOGGER.info("Running with database '%s' (backend=%s)",
                    settings.DATABASES['default']['NAME'],
                    settings.DATABASES['default']['ENGINE'])
        super().ready()
        self.clear_cache()
        # Check for invalid settings
        self.cleanup_settings()
        # Set external_domain on raven
        from supervisr.core.models import Setting
        settings.RAVEN_CONFIG['tags']['external_domain'] = Setting.get('domain')
        settings.RAVEN_CONFIG['tags']['install_id'] = Setting.get('install_id')
        # Trigger startup signal
        from supervisr.core.signals import on_post_startup
        on_post_startup.send(sender=self, pid=os.getpid())

    def bootstrap(self):
        """Add permissions and settings"""
        permissions = PermissionBootstrapper()
        permissions.add(codename='core_product_can_create',
                        name='Can create supervisr_core Products')
        settings = SettingBootstrapper()
        settings.add(key='signup:enabled', value=True)
        settings.add(key='password_reset:enabled', value=True)
        settings.add(key='signin:enabled', value=True)
        settings.add(key='banner:enabled', value=False)
        settings.add(key='account:email:required', value=True)
        settings.add(key='banner:level', value='info')
        settings.add(key='banner:message', value='')
        settings.add(key='branding', value='supervisr')
        settings.add(key='branding:icon', value='')
        settings.add(key='domain', value='http://localhost/')
        settings.add(key='recaptcha:enabled', value=False)
        settings.add(key='recaptcha:private', value='')
        settings.add(key='recaptcha:public', value='')
        settings.add(key='install_id', value=uuid.uuid4())
        settings.add(key='setup:is_fresh_install', value=True)
        settings.add(key='password:filter', value=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)'
                                                  r'(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}')
        settings.add(key='password:filter:description', value='Minimum 8 characters at least 1 '
                                                              'Uppercase Alphabet, 1 Lowercase '
                                                              'Alphabet, 1 Number and 1 Special '
                                                              'Character')
        return permissions, settings

    def cleanup_settings(self):
        """Cleanup settings without namespace or key"""
        try:
            from supervisr.core.models import Setting
            for setting in Setting.objects.all():
                if setting.namespace == '' or \
                        setting.key == '':
                    setting.delete()
        except (OperationalError, ProgrammingError, InternalError):
            pass
