"""
Supervisr Core Signal definitions
"""
from django.dispatch import Signal

SIG_USER_PRODUCT_RELATIONSHIP_CREATED = Signal(providing_args=['upr'])
SIG_USER_PRODUCT_RELATIONSHIP_DELETED = Signal(providing_args=['upr'])

SIG_USER_SIGNED_UP = Signal(providing_args=['user', 'req'])
SIG_USER_CHANGED_PASS = Signal(providing_args=['user', 'req', 'was_reset'])
SIG_USER_PASS_RESET_INIT = Signal(providing_args=['user'])
SIG_USER_PASS_RESET_FIN = Signal(providing_args=['user'])
SIG_USER_LOGIN = Signal(providing_args=['user, req'])
SIG_USER_LOGOUT = Signal(providing_args=['user, req'])
SIG_USER_RESEND_CONFIRM = Signal(providing_args=['user', 'req'])
