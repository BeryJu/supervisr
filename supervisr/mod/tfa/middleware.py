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

        if req.user.is_authenticated and \
            user_has_device(req.user) and \
            not req.user.is_verified() and \
            req.path != reverse('tfa:tfa-verify') and \
            not req.META.get('HTTP_AUTHORIZATION', '').startswith('Bearer'):
            # User has 2FA set up but is not verified

            # At this point the request is already forwarded to the target destination
            # So we just add the current request's path as next parameter
            args = '?next=%s' % req.get_full_path()
            return redirect(reverse('tfa:tfa-verify')+args)

        response = get_response(req)
        return response

    return middleware
