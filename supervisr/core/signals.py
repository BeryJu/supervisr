"""
Supervisr Core Signal definitions
"""

import logging

from django.db.models.signals import post_migrate, post_save, pre_delete
from django.dispatch import Signal, receiver
from passlib.hash import sha512_crypt

from supervisr.core.apps import SupervisrAppConfig
from supervisr.core.errors import SignalException

LOGGER = logging.getLogger(__name__)


class RobustSignal(Signal):
    """
    Signal Class that raises Exceptions in a child class
    """

    def send(self, sender, **named):
        results = super(RobustSignal, self).send_robust(sender, **named)
        for handler, result in results:
            if isinstance(result, Exception):
                raise SignalException("Handler %s: %s" %
                                      (handler.__name__, repr(result))) from result
        return results


SIG_USER_ACQUIRABLE_RELATIONSHIP_CREATED = RobustSignal(providing_args=['relationship'])
SIG_USER_ACQUIRABLE_RELATIONSHIP_DELETED = RobustSignal(providing_args=['relationship'])

SIG_USER_SIGN_UP = RobustSignal(providing_args=['user', 'request', 'password'])
SIG_USER_CHANGE_PASS = RobustSignal(providing_args=['user', 'request', 'password'])
SIG_USER_POST_SIGN_UP = RobustSignal(providing_args=['user', 'request'])
SIG_USER_POST_CHANGE_PASS = RobustSignal(providing_args=['user', 'request', 'was_reset'])
SIG_USER_PASS_RESET_INIT = RobustSignal(providing_args=['user'])
SIG_USER_PASS_RESET_FIN = RobustSignal(providing_args=['user'])
SIG_USER_CONFIRM = RobustSignal(providing_args=['user', 'request'])
SIG_USER_RESEND_CONFIRM = RobustSignal(providing_args=['user', 'request'])

SIG_DOMAIN_CREATED = RobustSignal(providing_args=['domain'])

# Signal which can be subscribed to initialize things that take longer
# and should not be run up on reboot of the app
SIG_DO_SETUP = RobustSignal(providing_args=['app_name'])
SIG_SETTING_UPDATE = RobustSignal(providing_args=[])

# SIG_CHECK_* Signals return a boolean

# Return wether user with `email` exists
SIG_CHECK_USER_EXISTS = RobustSignal(providing_args=['email'])

# SIG_GET_* Signals return something other than a boolean

# Return a hash for the /about/info page
SIG_GET_MOD_INFO = RobustSignal(providing_args=[])
# Get information for health status
SIG_GET_MOD_HEALTH = RobustSignal(providing_args=[])


# Set a statistic
SIG_SET_STAT = RobustSignal(providing_args=['key', 'value'])

@receiver(post_migrate)
# pylint: disable=unused-argument
def core_handle_post_migrate(sender, *args, **kwargs):
    """Trigger SIG_DO_SETUP"""
    if isinstance(sender, SupervisrAppConfig):
        LOGGER.debug("Running Post-Migrate for '%s'...", sender.name)
        sender.run_ensure_settings()
        SIG_DO_SETUP.send(sender.name)

@receiver(SIG_USER_CHANGE_PASS)
# pylint: disable=unused-argument
def crypt6_handle_user_change_pass(signal, user, password, **kwargs):
    """Update crypt6_password"""
    # Also update user's crypt6_pass
    user.crypt6_password = sha512_crypt.hash(password)
    user.save()

@receiver(SIG_SET_STAT)
# pylint: disable=unused-argument
def stat_output_verbose(signal, key, value, **kwargs):
    """Output stats to LOGGER"""
    LOGGER.debug("Stats: '%s': %r", key, value)

@receiver(post_save)
# pylint: disable=unused-argument
def change_on_save(sender, instance, created, **kwargs):
    """Forward signal to ChangeBuilder"""
    from supervisr.core.providers.change import ChangeBuilder
    from supervisr.core.models import ProviderAcquirable, ProviderAcquirableSingle

    change = ChangeBuilder()
    if issubclass(instance.__class__, ProviderAcquirable) and \
        instance.__class__ is not ProviderAcquirable:
        change.on_model_saved(instance, instance.providers, created)
    elif issubclass(instance.__class__, ProviderAcquirableSingle) and \
        instance.__class__ is not ProviderAcquirableSingle:
        change.on_model_saved(instance, [instance.provider_instance, ], created)

@receiver(pre_delete)
# pylint: disable=unused-argument
def change_on_delete(sender, instance, *args, **kwargs):
    """Forward signal to ChangeBuilder"""
    from supervisr.core.providers.change import ChangeBuilder
    from supervisr.core.models import ProviderAcquirable, ProviderAcquirableSingle

    change = ChangeBuilder()
    if issubclass(instance.__class__, ProviderAcquirable) and \
        instance.__class__ is not ProviderAcquirable:
        change.on_model_deleted(instance, instance.providers)
    elif issubclass(instance.__class__, ProviderAcquirableSingle) and \
        instance.__class__ is not ProviderAcquirableSingle:
        change.on_model_deleted(instance, [instance.provider_instance, ])
