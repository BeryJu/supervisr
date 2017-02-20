"""
Supervisr Core Signal definitions
"""
from django.dispatch import Signal

SIG_USER_PRODUCT_RELATIONSHIP_CREATED = Signal(providing_args=['upr'])
SIG_USER_PRODUCT_RELATIONSHIP_DELETED = Signal(providing_args=['upr'])

SIG_USER_SIGN_UP = Signal(providing_args=['user', 'req', 'password'])
SIG_USER_CHANGE_PASS = Signal(providing_args=['user', 'req', 'password'])
SIG_USER_POST_SIGN_UP = Signal(providing_args=['user', 'req'])
SIG_USER_POST_CHANGE_PASS = Signal(providing_args=['user', 'req', 'was_reset'])
SIG_USER_PASS_RESET_INIT = Signal(providing_args=['user'])
SIG_USER_PASS_RESET_FIN = Signal(providing_args=['user'])
SIG_USER_CONFIRM = Signal(providing_args=['user', 'req'])
SIG_USER_LOGIN = Signal(providing_args=['user, req'])
SIG_USER_LOGOUT = Signal(providing_args=['user, req'])
SIG_USER_RESEND_CONFIRM = Signal(providing_args=['user', 'req'])

# SIG_CHECK_* Signals return a boolean

# Return wether user with `email` exists
SIG_CHECK_USER_EXISTS = Signal(providing_args=['email'])

# SIG_GET_* Signals return something other than a boolean

# Return a hash for the /about/info page
SIG_GET_MOD_INFO = Signal(providing_args=[])
