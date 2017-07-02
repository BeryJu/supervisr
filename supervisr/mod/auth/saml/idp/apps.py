"""
Supervisr mod saml_idp app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModAuthSAMLProvider(SupervisrAppConfig):
    """
    Supervisr mod saml_idp app config
    """

    name = 'supervisr.mod.auth.saml.idp'
    title_moddifier = lambda self, title, request: 'SAML2/IDP'
    admin_url_name = 'supervisr/mod/auth/saml/idp:admin_settings'
