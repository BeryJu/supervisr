"""
Supervisr Core Common Views
"""

import sys

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from supervisr.core.api.utils import api_response
from supervisr.core.models import (Event, ProviderInstance,
                                   UserProductRelationship)


@login_required
def index(request):
    """Show index view with hosted_applications quicklaunch and recent events"""
    user_products = UserProductRelationship.objects.filter(user=request.user)
    hosted_applications = UserProductRelationship \
        .objects.filter(user=request.user, product__managed=True) \
        .exclude(product__management_url__isnull=True) \
        .exclude(product__management_url__exact='')
    events = Event.objects.filter(
        user=request.user, hidden=False) \
        .order_by('-create_date')[:15]
    user_providers = ProviderInstance.objects.filter(
        useracquirablerelationship__user__in=[request.user])
    # domains = Domain.objects.filter(users__in=[request.user])
    return render(request, 'common/index.html', {
        'uprs': user_products,
        'hosted_applications': hosted_applications,
        'events': events,
        'user_providers': user_providers,
        # 'domains': domains,
    })

# pylint: disable=unused-argument
def uncaught_404(request, **kwargs):
    """Handle an uncaught 404"""
    if 'api' in request.path:
        # return a json/xml/yaml message if this was an api call
        return api_response(request, {'message': 'not_found'})
    return render(request, 'common/error.html', {'code': 404})

# pylint: disable=unused-argument
def uncaught_500(request, **kwargs):
    """Handle an uncaught 500"""
    exc = sys.exc_info()
    message = None
    if exc:
        message = exc[1]

    if 'api' in request.path:
        # return a json/xml/yaml message if this was an api call
        return api_response(request, {'message': 'unexpected_error'})
    return render(request, 'common/error.html', {'code': 500, 'exc_message': message})

def error_response(request, message):
    """Show an error view with message"""
    if 'api' in request.path:
        # return a json/xml/yaml message if this was an api call
        return api_response(request, {'message': message})
    return render(request, 'common/error.html', {'code': 500, 'message': message})
