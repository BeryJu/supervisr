"""
Supervisr mod_ldap Models
"""

from django.db import models

from supervisr.fields import JSONField
from supervisr.models import CreatedUpdatedModel, PurgeableModel


class LDAPModification(CreatedUpdatedModel, PurgeableModel):
    """
    Store LDAP Data in DB if LDAP Server is unavailable
    """
    ACTION_ADD = 'ADD'
    ACTION_MODIFY = 'MODIFY'

    ACTIONS = (
        (ACTION_ADD, 'ADD'),
        (ACTION_MODIFY, 'MODIFY'),
    )

    ldap_moddification_id = models.AutoField(primary_key=True)
    dn = models.CharField(max_length=255) # pylint: disable=invalid-name
    action = models.CharField(max_length=17, choices=ACTIONS, default=ACTION_MODIFY)
    data = JSONField()
