"""
Supervisr 2FA AppConfig
"""


from supervisr.apps import SupervisrAppConfig


class SupervisrMod2FaConfig(SupervisrAppConfig):
    """
    Supervisr 2FA AppConfig
    """

    name = 'supervisr_mod_2fa'
    view_user_settings = 'tfa-user_settings'
