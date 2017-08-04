"""
Supervisr Core Common Views
"""

import sys

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from supervisr.core.models import (Event, ProviderInstance,
                                   UserProductRelationship)
from supervisr.core.views.api.utils import api_response


@login_required
def index(req):
    """
    Show index view with hosted_applications quicklaunch and recent events
    """
    user_products = UserProductRelationship.objects.filter(user=req.user)
    hosted_applications = UserProductRelationship \
        .objects.filter(user=req.user, product__managed=True) \
        .exclude(product__management_url__isnull=True) \
        .exclude(product__management_url__exact='')
    events = Event.objects.filter(
        user=req.user, hidden=False) \
        .order_by('-create_date')[:15]
    user_providers = ProviderInstance.objects.filter(
        userproductrelationship__user__in=[req.user])
    # domains = Domain.objects.filter(users__in=[req.user])
    return render(req, 'common/index.html', {
        'uprs': user_products,
        'hosted_applications': hosted_applications,
        'events': events,
        'user_providers': user_providers,
        # 'domains': domains,
    })

def uncaught_404(req):
    """
    Handle an uncaught 404
    """
    if 'api' in req.path:
        # return a json/xml/yaml message if this was an api call
        return api_response(req, {'message': 'not_found'})
    return render(req, 'common/error.html', {'code': 404})

def uncaught_500(req):
    """
    Handle an uncaught 500
    """
    exc = sys.exc_info()
    message = None
    if exc:
        message = exc[1]

    if 'api' in req.path:
        # return a json/xml/yaml message if this was an api call
        return api_response(req, {'message': 'unexpected_error'})
    return render(req, 'common/error.html', {'code': 500, 'exc_message': message})

def error_response(req, message):
    """
    Show an error view with message
    """
    if 'api' in req.path:
        # return a json/xml/yaml message if this was an api call
        return api_response(req, {'message': message})
    return render(req, 'common/error.html', {'code': 500, 'message': message})
