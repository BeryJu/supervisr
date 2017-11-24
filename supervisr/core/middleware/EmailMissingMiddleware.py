"""Supervisr Core Middleware to check if user has an email address"""

from django.shortcuts import redirect
from django.urls import reverse


def check_email(get_response):
    """Middleware to check if user has an email address"""

    def middleware(req):
        """Middleware to check if user has an email address"""
        if req.user.is_authenticated and req.user.email == '':
            return redirect(reverse('accounts-email-missing'))
        response = get_response(req)
        return response
    return middleware
