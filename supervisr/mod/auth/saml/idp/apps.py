"""
Supervisr mod saml_idp app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModAuthSAMLProvider(SupervisrAppConfig):
    """
    Supervisr mod saml_idp app config
    """

    name = 'supervisr.mod.auth.saml.idp'
    label = 'supervisr/mod/auth/saml/idp'
    verbose_name = 'Supervisr mod/auth/saml/idp'
    title_moddifier = lambda self, title, request: 'SAML2/IDP'
    admin_url_name = 'supervisr/mod/auth/saml/idp:admin_settings'
    init_modules = [
        'processors.demo',
        'processors.shib',
        'processors.salesforce',
        'processors.gitlab',
        'processors.generic',
        'processors.nextcloud',
        'models',
        ]

    def ensure_settings(self):
        from supervisr.core.models import Setting
        domain = Setting.get('domain')
        return {
            'issuer': domain,
            'certificate': '',
            'private_key': '',
            'signing': True,
            'autosubmit': True,
        }
