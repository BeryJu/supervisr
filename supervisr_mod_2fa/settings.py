"""
Supervisr 2FA Settings
"""

OTP_LOGIN_URL = 'supervisr_mod_2fa:tfa-verify'
OTP_TOTP_ISSUER = 'supervisr'
MIDDLEWARE = [
    'django_otp.middleware.OTPMiddleware',
    'supervisr_mod_2fa.middleware.tfa_force_verify',
]
INSTALLED_APPS = [
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
]