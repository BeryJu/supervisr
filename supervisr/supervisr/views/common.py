"""
Supervisr Core Common Views
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import Event, UserProductRelationship


@login_required
def index(req):
    """
    Show index view with hosted_applications quicklaunch and recent events
    """
    user_products = UserProductRelationship.objects.filter(user=req.user)
    hosted_applications = UserProductRelationship\
        .objects.filter(user=req.user, product__managed=True)
    events = Event.objects.filter(user=req.user)\
        .order_by('-create_date')[:15]
    return render(req, 'common/index.html', {
        'uprs': user_products,
        'hosted_applications': hosted_applications,
        'events': events
    })

def uncaught_404(req):
    """
    Handle an uncaught 404
    """
    return render(req, 'common/error.html', {'code': 404})

def uncaught_500(req):
    """
    Handle an uncaught 500
    """
    return render(req, 'common/error.html', {'code': 500})
