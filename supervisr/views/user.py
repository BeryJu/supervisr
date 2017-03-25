"""
Supervisr Core User Views
"""

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from ..models import Event, UserProductRelationship


@login_required
def index(req):
    """
    Show index view User informations
    """
    user_products = UserProductRelationship.objects.filter(user=req.user)
    hosted_applications = UserProductRelationship \
        .objects.filter(user=req.user, product__managed=True) \
        .exclude(product__management_url__isnull=True) \
        .exclude(product__management_url__exact='')
    event_list = Event.objects.filter(
        user=req.user, hidden=False) \
        .order_by('-create_date')[:15]
    # domains = Domain.objects.filter(users__in=[req.user])
    return render(req, 'user/index.html', {
        'uprs': user_products,
        'hosted_applications': hosted_applications,
        'events': event_list,
        # 'domains': domains,
    })

@login_required
def events(req):
    """
    Show a paginated list of all events
    """
    event_list = Event.objects.filter(
        user=req.user, hidden=False).order_by('-create_date')
    paginator = Paginator(event_list, 25)

    page = req.GET.get('page')
    try:
        event_page = paginator.page(page)
    except PageNotAnInteger:
        event_page = paginator.page(1)
    except EmptyPage:
        event_page = paginator.page(paginator.num_pages)

    return render(req, 'user/events.html', {'events': event_page})
