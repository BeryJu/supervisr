"""Supervisr mod_ldap app config"""

from supervisr.core.apps import SettingBootstrapper, SupervisrAppConfig


class SupervisrModAuthLDAPConfig(SupervisrAppConfig):
    """Supervisr mod_ldap app config"""

    name = 'supervisr.mod.auth.ldap'
    label = 'supervisr_mod_auth_ldap'
    title_modifier = lambda self, request: 'LDAP'
    admin_url_name = 'supervisr_mod_auth_ldap:admin_settings'
    verbose_name = 'Supervisr mod_auth_ldap'

    def bootstrap(self):
        settings = SettingBootstrapper()
        settings.add(key='enabled', value=False)
        settings.add(key='mode', value=0)
        settings.add(key='server', value='')
        settings.add(key='server:tls', value=False)
        settings.add(key='base', value='')
        settings.add(key='create_base', value='')
        settings.add(key='bind:user', value='')
        settings.add(key='bind:password', value='')
        settings.add(key='domain', value='')
        return (settings, )
