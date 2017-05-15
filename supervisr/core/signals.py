"""
Supervisr Core Signal definitions
"""

import logging

from django.db.models.signals import post_migrate
from django.dispatch import Signal, receiver

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


SIG_USER_PRODUCT_RELATIONSHIP_CREATED = RobustSignal(providing_args=['upr'])
SIG_USER_PRODUCT_RELATIONSHIP_DELETED = RobustSignal(providing_args=['upr'])

SIG_USER_SIGN_UP = RobustSignal(providing_args=['user', 'req', 'password'])
SIG_USER_CHANGE_PASS = RobustSignal(providing_args=['user', 'req', 'password'])
SIG_USER_POST_SIGN_UP = RobustSignal(providing_args=['user', 'req'])
SIG_USER_POST_CHANGE_PASS = RobustSignal(providing_args=['user', 'req', 'was_reset'])
SIG_USER_PASS_RESET_INIT = RobustSignal(providing_args=['user'])
SIG_USER_PASS_RESET_FIN = RobustSignal(providing_args=['user'])
SIG_USER_CONFIRM = RobustSignal(providing_args=['user', 'req'])
SIG_USER_LOGIN = RobustSignal(providing_args=['user, req'])
SIG_USER_LOGOUT = RobustSignal(providing_args=['user, req'])
SIG_USER_RESEND_CONFIRM = RobustSignal(providing_args=['user', 'req'])

SIG_DOMAIN_CREATED = RobustSignal(providing_args=['domain'])

# Signal which can be subscribed to initialize things that take longer
# and should not be run up on reboot of the app
SIG_DO_SETUP = RobustSignal(providing_args=['app_name'])

# SIG_CHECK_* Signals return a boolean

# Return wether user with `email` exists
SIG_CHECK_USER_EXISTS = RobustSignal(providing_args=['email'])

# SIG_GET_* Signals return something other than a boolean

# Return a hash for the /about/info page
SIG_GET_MOD_INFO = RobustSignal(providing_args=[])

@receiver(post_migrate)
# pylint: disable=unused-argument
def core_handle_post_migrate(sender, *args, **kwargs):
    """
    Trigger SIG_DO_SETUP
    """
    if isinstance(sender, SupervisrAppConfig):
        LOGGER.info("Running Post-Migrate for '%s'...", sender.name)
        SIG_DO_SETUP.send(sender.name)
