"""
Supervisr mod_ldap Admin
"""

from supervisr.core.admin import admin_autoregister

admin_autoregister('supervisr/mod/auth/ldap')
