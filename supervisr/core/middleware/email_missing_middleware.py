"""Supervisr Core Middleware to check if user has an email address"""

from django.shortcuts import redirect
from django.urls import reverse


def check_email(get_response):
    """Middleware to check if user has an email address"""

    def middleware(request):
        """Middleware to check if user has an email address"""
        if request.user.is_authenticated and request.user.email == '':
            return redirect(reverse('accounts-email-missing'))
        response = get_response(request)
        return response
    return middleware
