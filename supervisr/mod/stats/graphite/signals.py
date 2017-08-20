"""
Supervisr Stats Graphite Signals
"""


from django.dispatch import receiver

from supervisr.core.models import Setting
from supervisr.core.signals import (SIG_DOMAIN_CREATED, SIG_GET_MOD_HEALTH,
                                    SIG_SET_STAT, SIG_USER_CONFIRM,
                                    SIG_USER_LOGIN, SIG_USER_LOGOUT,
                                    SIG_USER_PASS_RESET_FIN,
                                    SIG_USER_POST_CHANGE_PASS,
                                    SIG_USER_POST_SIGN_UP,
                                    SIG_USER_PRODUCT_RELATIONSHIP_CREATED,
                                    SIG_USER_PRODUCT_RELATIONSHIP_DELETED,
                                    SIG_USER_RESEND_CONFIRM)
from supervisr.mod.stats.graphite.graphite_client import GraphiteClient


@receiver(SIG_GET_MOD_HEALTH)
# pylint: disable=unused-argument,invalid-name
def stats_graphite_handle_health(sender, **kwargs):
    """
    Create initial settings needed
    """
    if Setting.get('enabled') == 'True':
        with GraphiteClient():
            return True
    else:
        return True

@receiver(SIG_USER_PRODUCT_RELATIONSHIP_CREATED)
# pylint: disable=unused-argument,invalid-name
def stats_graphite_handle_upr_created(sender, **kwargs):
    """
    Handle stats for SIG_USER_PRODUCT_RELATIONSHIP_CREATED
    """
    if Setting.get('enabled') == 'True':
        with GraphiteClient() as client:
            client.write('signal.upr.created', 1)

@receiver(SIG_USER_PRODUCT_RELATIONSHIP_DELETED)
# pylint: disable=unused-argument,invalid-name
def stats_graphite_handle_upr_deleted(sender, **kwargs):
    """
    Handle stats for SIG_USER_PRODUCT_RELATIONSHIP_DELETED
    """
    if Setting.get('enabled') == 'True':
        with GraphiteClient() as client:
            client.write('signal.upr.deleted', 1)

@receiver(SIG_USER_POST_SIGN_UP)
# pylint: disable=unused-argument,invalid-name
def stats_graphite_handle_user_post_sign_up(sender, **kwargs):
    """
    Handle stats for SIG_USER_POST_SIGN_UP
    """
    if Setting.get('enabled') == 'True':
        with GraphiteClient() as client:
            client.write('signal.user.sign_up', 1)

@receiver(SIG_USER_POST_CHANGE_PASS)
# pylint: disable=unused-argument,invalid-name
def stats_graphite_handle_user_post_change_pass(sender, **kwargs):
    """
    Handle stats for SIG_USER_POST_CHANGE_PASS
    """
    if Setting.get('enabled') == 'True':
        with GraphiteClient() as client:
            client.write('signal.user.change_pass', 1)

@receiver(SIG_USER_PASS_RESET_FIN)
# pylint: disable=unused-argument,invalid-name
def stats_graphite_handle_user_pass_reset_fin(sender, **kwargs):
    """
    Handle stats for SIG_USER_PASS_RESET_FIN
    """
    if Setting.get('enabled') == 'True':
        with GraphiteClient() as client:
            client.write('signal.user.reset_pass', 1)

@receiver(SIG_USER_CONFIRM)
# pylint: disable=unused-argument,invalid-name
def stats_graphite_handle_user_confirm(sender, **kwargs):
    """
    Handle stats for SIG_USER_CONFIRM
    """
    if Setting.get('enabled') == 'True':
        with GraphiteClient() as client:
            client.write('signal.user.confirm', 1)

@receiver(SIG_USER_LOGIN)
# pylint: disable=unused-argument,invalid-name
def stats_graphite_handle_user_login(sender, **kwargs):
    """
    Handle stats for SIG_USER_LOGIN
    """
    if Setting.get('enabled') == 'True':
        with GraphiteClient() as client:
            client.write('signal.user.login', 1)

@receiver(SIG_USER_LOGOUT)
# pylint: disable=unused-argument,invalid-name
def stats_graphite_handle_user_logout(sender, **kwargs):
    """
    Handle stats for SIG_USER_LOGOUT
    """
    if Setting.get('enabled') == 'True':
        with GraphiteClient() as client:
            client.write('signal.user.logout', 1)

@receiver(SIG_USER_RESEND_CONFIRM)
# pylint: disable=unused-argument,invalid-name
def stats_graphite_handle_user_resend_confirm(sender, **kwargs):
    """
    Handle stats for SIG_USER_RESEND_CONFIRM
    """
    if Setting.get('enabled') == 'True':
        with GraphiteClient() as client:
            client.write('signal.user.resend_confirm', 1)

@receiver(SIG_DOMAIN_CREATED)
# pylint: disable=unused-argument,invalid-name
def stats_graphite_handle_domain_create(sender, **kwargs):
    """
    Handle stats for SIG_DOMAIN_CREATE
    """
    if Setting.get('enabled') == 'True':
        with GraphiteClient() as client:
            client.write('signal.domain.create', 1)

@receiver(SIG_SET_STAT)
# pylint: disable=unused-argument,invalid-name
def stats_graphite_handle_set_stat(sender, key, value, **kwargs):
    """
    Handle stats for SET_STAT
    """
    if Setting.get('enabled') == 'True':
        with GraphiteClient() as client:
            client.write(key, value)
