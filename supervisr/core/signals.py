"""Supervisr Core Signal definitions"""


from django.db.models.signals import post_migrate, post_save, pre_delete
from django.dispatch import Signal, receiver
from passlib.hash import sha512_crypt

from supervisr.core.apps import SupervisrAppConfig
from supervisr.core.exceptions import SignalException
from supervisr.core.logger import SupervisrLogger

LOGGER = SupervisrLogger(__name__)


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

# SIG_CHECK_* Signals return a boolean

# Return wether user with `email` exists
on_check_user_exists = RobustSignal(providing_args=['email'])

# SIG_GET_* Signals return something other than a boolean

# Return a hash for the /about/info page
get_module_info = RobustSignal(providing_args=[])
# Get information for health status
get_module_health = RobustSignal(providing_args=[])


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
def change_on_save(sender, instance, created, **kwargs):
    """Forward signal to ChangeBuilder"""
    from supervisr.core.providers.multiplexer import ProviderMultiplexer
    from supervisr.core.models import ProviderAcquirable, ProviderAcquirableSingle, get_system_user

    system_user = get_system_user()
    multiplexer = ProviderMultiplexer()
    providers = []
    if issubclass(instance.__class__, ProviderAcquirable) and \
            instance.__class__ is not ProviderAcquirable:
        providers = instance.providers.all()
    elif issubclass(instance.__class__, ProviderAcquirableSingle) and \
            instance.__class__ is not ProviderAcquirableSingle:
        providers = [instance.provider_instance, ]
    if providers:
        multiplexer.on_model_saved(system_user, instance, providers, created)


@receiver(pre_delete)
# pylint: disable=unused-argument
def change_on_delete(sender, instance, *args, **kwargs):
    """Forward signal to ChangeBuilder"""
    from supervisr.core.providers.multiplexer import ProviderMultiplexer
    from supervisr.core.models import ProviderAcquirable, ProviderAcquirableSingle, get_system_user

    system_user = get_system_user()
    multiplexer = ProviderMultiplexer()
    providers = []
    if issubclass(instance.__class__, ProviderAcquirable) and \
            instance.__class__ is not ProviderAcquirable:
        providers = instance.providers.all()
    elif issubclass(instance.__class__, ProviderAcquirableSingle) and \
            instance.__class__ is not ProviderAcquirableSingle:
        providers = [instance.provider_instance, ]
    if providers:
        multiplexer.on_model_deleted(system_user, instance, providers)
