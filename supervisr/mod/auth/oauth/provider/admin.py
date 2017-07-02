"""
Supervisr oauth provider Admin
"""
from supervisr.core.admin import admin_autoregister

admin_autoregister('supervisr/mod/auth/oauth/provider')
