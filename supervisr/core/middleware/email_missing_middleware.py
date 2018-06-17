"""Supervisr Core Middleware to check if user has an email address"""

from django.shortcuts import redirect
from django.urls import reverse
from supervisr.core.models import Setting


def check_email(get_response):
    """Middleware to check if user has an email address"""

    redirect_url = reverse('accounts-email-missing')

    def middleware(request):
        """Middleware to check if user has an email address"""

        if request.user.is_authenticated and \
                request.user.email == '' and \
                Setting.get_bool('account:email:required') and \
                request.path_info != redirect_url:
            return redirect(redirect_url)
        response = get_response(request)
        return response
    return middleware
