"""Supervisr Core Signal definitions"""
from logging import getLogger

from django.db.models.signals import (m2m_changed, post_migrate, post_save,
                                      pre_delete)
from django.dispatch import Signal, receiver
from django.dispatch.dispatcher import NO_RECEIVERS

from supervisr.core.apps import SupervisrAppConfig
from supervisr.core.exceptions import SignalException
from supervisr.core.utils import class_to_path
from supervisr.core.utils.statistics import StatisticType, set_statistic

LOGGER = getLogger(__name__)


class RobustSignal(Signal):
    """Signal Class that raises Exceptions in a child class"""

    def __init__(self, stat_name=None, providing_args=None):
        super().__init__(providing_args=providing_args)
        self.stat_name = stat_name

    def send(self, sender, **named):
        if not self.receivers or self.sender_receivers_cache.get(sender) is NO_RECEIVERS:
            return []
        values = {}
        values['sent'] = {
            'value': 1,
            'type': StatisticType.Counter,
        }

        # Call each receiver with whatever arguments it can accept.
        # Return a list of tuple pairs [(receiver, response), ... ].
        responses = []
        for _receiver in self._live_receivers(sender):
            try:
                # We time the receiver call as well as count the call
                values['receiver.%s.call' % _receiver.__name__] = {
                    'value': 1,
                    'type': StatisticType.Counter
                }
                response = _receiver(signal=self, sender=sender, **named)

                if self.stat_name:
                    set_statistic(self.stat_name, hints={'category': 'event'}, **values)
            except Exception as err:
                raise SignalException("Handler %s: %s" %
                                      (_receiver.__name__, repr(err))) from err
            else:
                responses.append((_receiver, response))
        return responses


on_user_acquirable_relationship_created = RobustSignal(
    stat_name="on_user_acquirable_relationship_created", providing_args=['relationship'])
on_user_acquirable_relationship_deleted = RobustSignal(
    stat_name="on_user_acquirable_relationship_deleted", providing_args=['relationship'])

on_post_startup = RobustSignal(
    stat_name="on_post_startup", providing_args=['pid'])

on_domain_created = RobustSignal(
    stat_name="on_domain_created", providing_args=['domain'])

# Signal which can be subscribed to initialize things that take longer
# and should not be run up on reboot of the app
on_migration_post = RobustSignal(
    stat_name="on_migration_post", providing_args=['app_name'])
on_setting_update = RobustSignal(
    stat_name="on_setting_update", providing_args=[])

# get_* Signals return something other than a boolean

# Return a hash for the /about/info page
get_module_info = RobustSignal(
    stat_name="get_module_info", providing_args=[])
# Get information for health status
get_module_health = RobustSignal(
    stat_name="get_module_health", providing_args=[])

on_search = RobustSignal(
    stat_name="on_search", providing_args=['query', 'request'])

# Set a statistic
on_set_statistic = RobustSignal(providing_args=['name', 'values', 'hints'])


@receiver(post_migrate)
# pylint: disable=unused-argument
def core_handle_post_migrate(sender, *args, **kwargs):
    """Trigger SIG_DO_SETUP"""
    if isinstance(sender, SupervisrAppConfig):
        LOGGER.debug("Running Post-Migrate for '%s'...", sender.name)
        sender.run_bootstrap()
        on_migration_post.send(sender.name)


@receiver(on_set_statistic)
# pylint: disable=unused-argument
def stat_output_verbose(signal, name, values, hints, **kwargs):
    """Output stats to LOGGER"""
    LOGGER.debug("'%s': %r (hints=%r)", name, values, hints)


@receiver(post_save)
# pylint: disable=unused-argument
def provider_post_save(sender, instance, created, **kwargs):
    """Forward signal to ChangeBuilder"""
    from supervisr.core.providers.multiplexer import ProviderMultiplexer
    from supervisr.core.providers.objects import ProviderAction
    from supervisr.core.models import ProviderTriggerMixin

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
    from supervisr.core.models import ProviderTriggerMixin

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


@receiver(pre_delete)
# pylint: disable=unused-argument
def relationship_pre_delete(sender, instance, **kwargs):
    """Send signal when relationship is deleted"""
    from django.contrib.auth.models import UserAcquirableRelationship
    if sender == UserAcquirableRelationship:
        # Send signal to we are going to be deleted
        on_user_acquirable_relationship_deleted.send(
            sender=UserAcquirableRelationship,
            relationship=instance)

@receiver(post_save)
# pylint: disable=unused-argument
def send_create(sender, signal, instance, created, **kwargs):
    """Send Model creation signal"""
    from supervisr.core.models import Domain, UserAcquirableRelationship, Setting
    if sender == Domain and created:
        on_domain_created.send(
            sender=Domain,
            domain=instance)
    elif sender == UserAcquirableRelationship and created:
        on_user_acquirable_relationship_created.send(
            sender=UserAcquirableRelationship,
            relationship=instance)
    elif sender == Setting:
        on_setting_update.send(sender=Setting, setting=instance)
