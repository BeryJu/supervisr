"""Supervisr 2FA AppConfig"""


from supervisr.core.apps import SupervisrAppConfig


class SupervisrModTFAConfig(SupervisrAppConfig):
    """Supervisr TFA AppConfig"""

    name = 'supervisr.mod.tfa'
    label = 'supervisr_mod_tfa'
    view_user_settings = 'tfa-user_settings'
    title_modifier = lambda self, request: '2FA'
