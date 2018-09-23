"""Supervisr Stats influx Signals"""


from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from supervisr.core.models import Setting
from supervisr.core.signals import (get_module_health, on_domain_created,
                                    on_set_statistic,
                                    on_user_acquirable_relationship_created,
                                    on_user_acquirable_relationship_deleted,
                                    on_user_change_password_post,
                                    on_user_confirm_resend, on_user_confirmed,
                                    on_user_password_reset_finish,
                                    on_user_sign_up_post)
from supervisr.mod.stats.influx.influx_client import InfluxClient


@receiver(get_module_health)
# pylint: disable=unused-argument
def stats_influx_handle_health(sender, **kwargs):
    """Create initial settings needed"""
    if Setting.get_bool('enabled'):
        with InfluxClient():
            return True
    else:
        return True


@receiver(on_user_acquirable_relationship_created)
# pylint: disable=unused-argument
def stats_influx_handle_releationship_created(sender, relationship, **kwargs):
    """Handle stats for SIG_USER_ACQUIRABLE_RELATIONSHIP_CREATED"""
    if Setting.get_bool('enabled'):
        with InfluxClient() as client:
            client.write('signal',
                         tags={
                             'kind': 'relationship',
                             'action': 'created',
                             'user': 'Anonymous' if relationship.user.username == ''
                                     else relationship.user.username,
                         },
                         count=1)


@receiver(on_user_acquirable_relationship_deleted)
# pylint: disable=unused-argument
def stats_influx_handle_releationship_deleted(sender, relationship, **kwargs):
    """Handle stats for SIG_USER_ACQUIRABLE_RELATIONSHIP_DELETED"""
    if Setting.get_bool('enabled'):
        with InfluxClient() as client:
            client.write('signal',
                         tags={
                             'kind': 'relationship',
                             'action': 'deleted',
                             'user': 'Anonymous' if relationship.user.username == ''
                                     else relationship.user.username,
                         },
                         count=1)


@receiver(on_user_sign_up_post)
# pylint: disable=unused-argument
def stats_influx_handle_user_post_sign_up(sender, user, **kwargs):
    """Handle stats for SIG_USER_POST_SIGN_UP"""
    if Setting.get_bool('enabled'):
        with InfluxClient() as client:
            client.write('signal',
                         tags={
                             'kind': 'user',
                             'action': 'sign_up',
                             'user': 'Anonymous' if user.username == '' else user.username,
                         },
                         count=1)


@receiver(on_user_change_password_post)
# pylint: disable=unused-argument
def stats_influx_handle_user_post_change_pass(sender, user, **kwargs):
    """Handle stats for SIG_USER_POST_CHANGE_PASS"""
    if Setting.get_bool('enabled'):
        with InfluxClient() as client:
            client.write('signal',
                         tags={
                             'kind': 'user',
                             'action': 'change_pass',
                             'user': 'Anonymous' if user.username == '' else user.username,
                         },
                         count=1)


@receiver(on_user_password_reset_finish)
# pylint: disable=unused-argument
def stats_influx_handle_user_pass_reset_fin(sender, user, **kwargs):
    """Handle stats for SIG_USER_PASS_RESET_FIN"""
    if Setting.get_bool('enabled'):
        with InfluxClient() as client:
            client.write('signal',
                         tags={
                             'kind': 'user',
                             'action': 'reset_pass',
                             'user': 'Anonymous' if user.username == '' else user.username,
                         },
                         count=1)


@receiver(on_user_confirmed)
# pylint: disable=unused-argument
def stats_influx_handle_user_confirm(sender, user, **kwargs):
    """Handle stats for SIG_USER_CONFIRM"""
    if Setting.get_bool('enabled'):
        with InfluxClient() as client:
            client.write('signal',
                         tags={
                             'kind': 'user',
                             'action': 'confirm',
                             'user': 'Anonymous' if user.username == '' else user.username,
                         },
                         count=1)


@receiver(user_logged_in)
# pylint: disable=unused-argument
def stats_influx_handle_user_login(sender, user, **kwargs):
    """Handle stats for user_logged_in"""
    if Setting.get_bool('enabled'):
        with InfluxClient() as client:
            client.write('signal',
                         tags={
                             'kind': 'user',
                             'action': 'login',
                             'user': 'Anonymous' if user.username == '' else user.username,
                         },
                         count=1)


@receiver(user_logged_out)
# pylint: disable=unused-argument
def stats_influx_handle_user_logout(sender, user, **kwargs):
    """Handle stats for user_logged_out"""
    if Setting.get_bool('enabled'):
        with InfluxClient() as client:
            client.write('signal',
                         tags={
                             'kind': 'user',
                             'action': 'logout',
                             'user': 'Anonymous' if user.username == '' else user.username,
                         },
                         count=1)


@receiver(on_user_confirm_resend)
# pylint: disable=unused-argument
def stats_influx_handle_user_resend_confirm(sender, user, **kwargs):
    """Handle stats for SIG_USER_RESEND_CONFIRM"""
    if Setting.get_bool('enabled'):
        with InfluxClient() as client:
            client.write('signal',
                         tags={
                             'kind': 'user',
                             'action': 'resend_confirm',
                             'user': 'Anonymous' if user.username == '' else user.username,
                         },
                         count=1)


@receiver(on_domain_created)
# pylint: disable=unused-argument
def stats_influx_handle_domain_create(sender, **kwargs):
    """Handle stats for SIG_DOMAIN_CREATE"""
    if Setting.get_bool('enabled'):
        with InfluxClient() as client:
            client.write('signal',
                         tags={
                             'kind': 'domain',
                             'action': 'create'
                         },
                         count=1)


@receiver(on_set_statistic)
# pylint: disable=unused-argument
def stats_influx_handle_set_stat(sender, key, value, **kwargs):
    """Handle stats for SET_STAT"""
    if Setting.get_bool('enabled'):
        with InfluxClient() as client:
            client.write('stat', **{key: value})
