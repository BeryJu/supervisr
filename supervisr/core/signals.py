"""
Supervisr Core Signal definitions
"""

from django.dispatch import Signal

from .errors import SignalException


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

# SIG_CHECK_* Signals return a boolean

# Return wether user with `email` exists
SIG_CHECK_USER_EXISTS = RobustSignal(providing_args=['email'])

# SIG_GET_* Signals return something other than a boolean

# Return a hash for the /about/info page
SIG_GET_MOD_INFO = RobustSignal(providing_args=[])