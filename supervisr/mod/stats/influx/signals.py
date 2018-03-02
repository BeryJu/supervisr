"""
Supervisr Stats influx Signals
"""


from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from supervisr.core.models import Setting
from supervisr.core.signals import (SIG_DOMAIN_CREATED, SIG_GET_MOD_HEALTH,
                                    SIG_SET_STAT,
                                    SIG_USER_ACQUIRABLE_RELATIONSHIP_CREATED,
                                    SIG_USER_ACQUIRABLE_RELATIONSHIP_DELETED,
                                    SIG_USER_CONFIRM, SIG_USER_PASS_RESET_FIN,
                                    SIG_USER_POST_CHANGE_PASS,
                                    SIG_USER_POST_SIGN_UP,
                                    SIG_USER_RESEND_CONFIRM)
from supervisr.mod.stats.influx.influx_client import InfluxClient


@receiver(SIG_GET_MOD_HEALTH)
# pylint: disable=unused-argument
def stats_influx_handle_health(sender, **kwargs):
    """Create initial settings needed"""
    if Setting.get_bool('enabled'):
        with InfluxClient():
            return True
    else:
        return True

@receiver(SIG_USER_ACQUIRABLE_RELATIONSHIP_CREATED)
# pylint: disable=unused-argument,invalid-name
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

@receiver(SIG_USER_ACQUIRABLE_RELATIONSHIP_DELETED)
# pylint: disable=unused-argument,invalid-name
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

@receiver(SIG_USER_POST_SIGN_UP)
# pylint: disable=unused-argument,invalid-name
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

@receiver(SIG_USER_POST_CHANGE_PASS)
# pylint: disable=unused-argument,invalid-name
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

@receiver(SIG_USER_PASS_RESET_FIN)
# pylint: disable=unused-argument,invalid-name
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

@receiver(SIG_USER_CONFIRM)
# pylint: disable=unused-argument,invalid-name
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

@receiver(SIG_USER_RESEND_CONFIRM)
# pylint: disable=unused-argument,invalid-name
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

@receiver(SIG_DOMAIN_CREATED)
# pylint: disable=unused-argument,invalid-name
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

@receiver(SIG_SET_STAT)
# pylint: disable=unused-argument
def stats_influx_handle_set_stat(sender, key, value, **kwargs):
    """Handle stats for SET_STAT"""
    if Setting.get_bool('enabled'):
        with InfluxClient() as client:
            client.write('stat', **{key: value})
