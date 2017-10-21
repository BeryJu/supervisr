"""
Supervisr 2FA AppConfig
"""


from supervisr.core.apps import SupervisrAppConfig


class SupervisrModTFAConfig(SupervisrAppConfig):
    """
    Supervisr TFA AppConfig
    """

    name = 'supervisr.mod.tfa'
    label = 'supervisr/mod/tfa'
    view_user_settings = 'tfa-user_settings'
    title_moddifier = lambda self, title, request: '2FA'
