"""
Supervisr Core Signal definitions
"""
from django.dispatch import Signal

SIG_USER_PRODUCT_RELATIONSHIP_CREATED = Signal(providing_args=['upr'])
SIG_USER_PRODUCT_RELATIONSHIP_DELETED = Signal(providing_args=['upr'])

SIG_USER_SIGNED_UP = Signal(providing_args=['user'])
SIG_USER_CHANGED_PASS = Signal(providing_args=['user', 'was_reset'])
