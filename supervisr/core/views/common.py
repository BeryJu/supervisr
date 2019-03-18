"""Supervisr Core Common Views"""

import sys

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from supervisr.core.models import ProviderInstance


class IndexView(LoginRequiredMixin, View):
    """Show index view with hosted_applications quicklaunch and recent events"""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Show index view with hosted_applications quicklaunch and recent events"""
        user_providers = ProviderInstance.objects.filter(
            useracquirablerelationship__user__in=[request.user])
        # domains = Domain.objects.filter(users__in=[request.user])
        return render(request, 'common/index.html', {
            'user_providers': user_providers,
            # 'domains': domains,
        })


class Uncaught404View(View):
    """Handle uncaught 404 errors"""

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handle an uncaught 404"""
        return render(request, 'common/error.html', {'code': 404}, status=404)


class Uncaught500View(View):
    """Handle uncaught 500 errors"""

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handle an uncaught 500"""
        exc = sys.exc_info()
        message = exc[1] if exc else None
        return render(request, 'common/error.html',
                      {'code': 500, 'exc_message': message}, status=500)


class ErrorResponseView(View):
    """Show an error view with message"""

    def dispatch(self, request: HttpRequest, *args, message, **kwargs) -> HttpResponse:
        """Show an error view with message"""
        return render(request, 'common/error.html', {'code': 500, 'message': message}, status=500)
