"""ldap temp settings"""

LDAP_FIELDS = {
    "username": "sAMAccountName",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

# LDAP_LOOKUP_FIELDS = ("sAMAccountName",)
# LDAP_LOOKUP_FIELDS = ("mail",)
LDAP_LOOKUP_FIELDS = ("userPrincipalName",)
