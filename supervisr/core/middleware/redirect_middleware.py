"""Supervisr Core Middleware to check various things and redirect the user"""

from django.shortcuts import redirect
from django.urls import resolve, reverse

from supervisr.core.models import Setting
from supervisr.core.utils import is_database_synchronized


def redirect_middleware(get_response):
    """Middleware to check various things and redirect the user"""

    email_redirect_url = reverse('accounts-email-missing')
    setup_redirect_url = reverse('setup', kwargs={'step': 'welcome'})

    def middleware(request):
        """Middleware to check various things and redirect the user"""
        resolver_match = resolve(request.path_info)
        # Check for first install
        if Setting.get_bool('setup:is_fresh_install', default=True) and \
                resolver_match.url_name != 'setup':
            return redirect(setup_redirect_url)

        # Check for pending updates
        if not is_database_synchronized() and \
                resolver_match.url_name != 'setup':
            return redirect(setup_redirect_url)

        # Check for missing email
        if request.user.is_authenticated and \
                request.user.email == '' and \
                Setting.get_bool('account:email:required') and \
                request.path_info != email_redirect_url:
            return redirect(email_redirect_url)

        response = get_response(request)
        return response
    return middleware
