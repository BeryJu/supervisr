"""Supervisr Core Signal definitions"""
from logging import getLogger

from django.db.models.signals import (m2m_changed, post_migrate, post_save,
                                      pre_delete)
from django.dispatch import Signal, receiver
from passlib.hash import sha512_crypt

from supervisr.core.apps import SupervisrAppConfig
from supervisr.core.exceptions import SignalException
from supervisr.core.utils import class_to_path

LOGGER = getLogger(__name__)


class RobustSignal(Signal):
    """Signal Class that raises Exceptions in a child class"""

    def send(self, sender, **named):
        results = super(RobustSignal, self).send_robust(sender, **named)
        for handler, result in results:
            if isinstance(result, Exception):
                raise SignalException("Handler %s: %s" %
                                      (handler.__name__, repr(result))) from result
        return results


on_user_acquirable_relationship_created = RobustSignal(providing_args=['relationship'])
on_user_acquirable_relationship_deleted = RobustSignal(providing_args=['relationship'])

on_user_sign_up = RobustSignal(
    providing_args=['user', 'request', 'password', 'needs_confirmation'])
on_user_change_password = RobustSignal(providing_args=['user', 'request', 'password'])
on_user_sign_up_post = RobustSignal(providing_args=['user', 'request', 'needs_confirmation'])
on_user_change_password_post = RobustSignal(providing_args=['user', 'request', 'was_reset'])
on_user_password_reset_init = RobustSignal(providing_args=['user'])
on_user_password_reset_finish = RobustSignal(providing_args=['user'])
on_user_confirmed = RobustSignal(providing_args=['user', 'request'])
on_user_confirm_resend = RobustSignal(providing_args=['user', 'request'])

on_domain_created = RobustSignal(providing_args=['domain'])

# Signal which can be subscribed to initialize things that take longer
# and should not be run up on reboot of the app
on_migration_post = RobustSignal(providing_args=['app_name'])
on_setting_update = RobustSignal(providing_args=[])

# on_check_* Signals return a boolean

# Return wether user with `email` exists
on_check_user_exists = RobustSignal(providing_args=['email'])

# get_* Signals return something other than a boolean

# Return a hash for the /about/info page
get_module_info = RobustSignal(providing_args=[])
# Get information for health status
get_module_health = RobustSignal(providing_args=[])

on_search = RobustSignal(providing_args=['query', 'request'])

# Set a statistic
on_set_statistic = RobustSignal(providing_args=['key', 'value'])


@receiver(post_migrate)
# pylint: disable=unused-argument
def core_handle_post_migrate(sender, *args, **kwargs):
    """Trigger SIG_DO_SETUP"""
    if isinstance(sender, SupervisrAppConfig):
        LOGGER.debug("Running Post-Migrate for '%s'...", sender.name)
        sender.run_bootstrap()
        on_migration_post.send(sender.name)


@receiver(on_user_change_password)
# pylint: disable=unused-argument
def crypt6_handle_user_change_pass(signal, user, password, **kwargs):
    """Update crypt6_password"""
    # Also update user's crypt6_pass
    user.crypt6_password = sha512_crypt.hash(password)
    user.save()


@receiver(on_set_statistic)
# pylint: disable=unused-argument
def stat_output_verbose(signal, key, value, **kwargs):
    """Output stats to LOGGER"""
    LOGGER.debug("Stats: '%s': %r", key, value)


@receiver(post_save)
# pylint: disable=unused-argument
def provider_post_save(sender, instance, created, **kwargs):
    """Forward signal to ChangeBuilder"""
    from supervisr.core.providers.multiplexer import ProviderMultiplexer
    from supervisr.core.providers.objects import ProviderAction
    from supervisr.core.models import ProviderTriggerMixin, get_system_user

    system_user = get_system_user()
    if issubclass(instance.__class__, ProviderTriggerMixin):
        LOGGER.debug("ProviderTriggerMixin post_save")
        args = (ProviderAction.SAVE, class_to_path(instance.__class__), instance.pk)
        kwargs = {'created': created}
        system_user.task_apply_async(ProviderMultiplexer(), *args, **kwargs)


@receiver(pre_delete)
# pylint: disable=unused-argument
def provider_pre_delete(sender, instance, **kwargs):
    """Forward signal to ChangeBuilder"""
    from supervisr.core.providers.multiplexer import ProviderMultiplexer
    from supervisr.core.providers.objects import ProviderAction
    from supervisr.core.models import ProviderTriggerMixin, get_system_user

    system_user = get_system_user()
    if issubclass(instance.__class__, ProviderTriggerMixin):
        LOGGER.debug("ProviderTriggerMixin pre_delete")
        args = (ProviderAction.DELETE, class_to_path(instance.__class__), instance.pk)
        system_user.task_apply_async(ProviderMultiplexer(), *args)


@receiver(m2m_changed)
def provider_m2m(sender, instance, action, **kwargs):
    """Trigger provider_post_save and provider_pre_delete from m2m updates"""
    from supervisr.core.models import ProviderTriggerMixin

    if issubclass(instance.__class__, ProviderTriggerMixin) or \
        issubclass(sender.__class__, ProviderTriggerMixin):

        if action == 'post_add':
            LOGGER.debug("m2m post_add (sender=%r, instance=%r)", sender, instance)
            provider_post_save(sender, instance, created=False, **kwargs)
        elif action == 'pre_remove':
            LOGGER.debug("m2m pre_delete (sender=%r, instance=%r)", sender, instance)
            provider_pre_delete(sender, instance, **kwargs)
