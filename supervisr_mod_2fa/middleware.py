"""
Supervisr 2FA Middleware to force users with 2FA set up to verify
"""

from django.shortcuts import redirect
from django.urls import reverse
from django_otp import user_has_device


def tfa_force_verify(get_response):
    """
    Middleware to force 2FA Verification
    """
    def middleware(req):
        """
        Middleware to force 2FA Verification
        """

        # Check if it's an oauth2 request, if so skip
        if request.META.get('HTTP_AUTHORIZATION', '').startswith('Bearer') or \
            req.user.is_verified():
            response = get_response(req)
            return response

        if req.user.is_authenticated and \
            user_has_device(req.user) and \
            not req.user.is_verified() and \
            req.path != reverse('supervisr_mod_2fa:tfa-verify'):
            # User has 2FA set up but is not verified
            return redirect(reverse('supervisr_mod_2fa:tfa-verify'))

    return middleware
