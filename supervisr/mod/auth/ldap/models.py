"""
Supervisr mod_ldap Models
"""

from django.contrib.auth.models import Group
from django.db import models

from supervisr.core.fields import JSONField
from supervisr.core.models import CreatedUpdatedModel, ProductExtension


class LDAPModification(CreatedUpdatedModel):
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
    dn = models.CharField(max_length=255)
    action = models.CharField(max_length=17, choices=ACTIONS, default=ACTION_MODIFY)
    data = JSONField()

    def __str__(self):
        return "LDAPModification %d from %s" % (self.ldap_moddification_id, self.created)


class LDAPGroupMapping(CreatedUpdatedModel):
    """Model to map an LDAP Group to a supervisr group"""

    ldap_dn = models.TextField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return "LDAPGroupMapping %s -> %s" % (self.ldap_dn, self.group.name)


class ProductExtensionLDAP(ProductExtension):
    """
    Save LDAP group to a product
    """

    ldap_group = models.TextField(blank=True)
