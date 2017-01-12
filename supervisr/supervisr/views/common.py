from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import *

@login_required
def index(req):
    user_products = UserProductRelationship.objects.filter(user=req.user)
    hosted_applications = UserProductRelationship\
        .objects.filter(user=req.user,product__managed=True)
    events = Event.objects.filter(user=req.user)\
        .order_by('-create_date')[:15]
    return render(req, 'common/index.html', {
        'uprs': user_products,
        'hosted_applications': hosted_applications,
        'events': events
    })

def uncaught_404(req):
    return render(req, 'common/error.html', { 'code': 404 })

def uncaught_500(req):
    return render(req, 'common/error.html', { 'code': 500 })
