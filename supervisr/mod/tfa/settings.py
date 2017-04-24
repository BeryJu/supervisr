"""
Supervisr 2FA Settings
"""

OTP_LOGIN_URL = 'tfa:tfa-verify'
OTP_TOTP_ISSUER = 'supervisr'
MIDDLEWARE = [
    'django_otp.middleware.OTPMiddleware',
    'supervisr.mod.tfa.middleware.tfa_force_verify',
]
INSTALLED_APPS = [
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
]
