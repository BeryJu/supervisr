"""
Supervisr 2FA AppConfig
"""


from supervisr.apps import SupervisrAppConfig


class SupervisrMod2FaConfig(SupervisrAppConfig):
    """
    Supervisr 2FA AppConfig
    """

    name = 'supervisr_mod_2fa'
    inject_middleware = ['django_otp.middleware.OTPMiddleware']
