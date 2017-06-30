"""
Supervisr mod saml_idp app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModSAMLIDPConfig(SupervisrAppConfig):
    """
    Supervisr mod saml_idp app config
    """

    name = 'supervisr.mod.saml.idp'
    title_moddifier = lambda self, title, request: 'SAML2/IDP'
    admin_url_name = 'saml/idp:admin_settings'
