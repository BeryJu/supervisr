"""
SAML IDP Admin
"""

from supervisr.core.admin import admin_autoregister

admin_autoregister('supervisr/mod/auth/saml/idp')
