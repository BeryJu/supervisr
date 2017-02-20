"""
Supervisr mod_ldap Models
"""

from django.db import models

from supervisr.fields import JSONField
from supervisr.models import PurgeableModel


class LDAPModification(PurgeableModel):
    """
    Store LDAP Data in DB if LDAP Server is unavailable
    """
    ACTION_MODIFY_ADD = 'MODIFY_ADD'
    ACTION_MODIFY_DELETE = 'MODIFY_DELETE'
    ACTION_MODIFY_REPLACE = 'MODIFY_REPLACE'
    ACTION_MODIFY_INCREMENT = 'MODIFY_INCREMENT'

    ACTIONS = (
        (ACTION_MODIFY_ADD, 'MODIFY_ADD'),
        (ACTION_MODIFY_DELETE, 'MODIFY_DELETE'),
        (ACTION_MODIFY_REPLACE, 'MODIFY_REPLACE'),
        (ACTION_MODIFY_INCREMENT, 'MODIFY_INCREMENT'),
    )

    ldap_moddification_id = models.AutoField(primary_key=True)
    dn = models.CharField(max_length=255) # pylint: disable=invalid-name
    action = models.CharField(max_length=17, choices=ACTIONS)
    data = JSONField()
