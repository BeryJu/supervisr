"""Supervisr mod saml_idp app config"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModAuthSAMLProvider(SupervisrAppConfig):
    """Supervisr mod saml_idp app config"""

    name = 'supervisr.mod.auth.saml.idp'
    label = 'supervisr_mod_auth_saml_idp'
    verbose_name = 'Supervisr mod_auth_saml_idp'
    title_modifier = lambda self, request: 'SAML2/IDP'
    admin_url_name = 'supervisr_mod_auth_saml_idp:admin_settings'
    init_modules = [
        'processors.demo',
        'processors.shib',
        'processors.salesforce',
        'processors.gitlab',
        'processors.generic',
        'processors.nextcloud',
        'processors.wordpress_orange',
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
            'assertion_valid_for': 15
        }
