"""
Supervisr Core Common Views
"""

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.utils.safestring import mark_safe

from ..models import Event, UserProductRelationship
from ..utils import do_404, render_to_string


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
    # domains = Domain.objects.filter(users__in=[req.user])
    return render(req, 'common/index.html', {
        'uprs': user_products,
        'hosted_applications': hosted_applications,
        'events': events,
        # 'domains': domains,
    })

@login_required
def search(req):
    """
    Searching of models and subapps
    """
    if 'q' in req.GET:
        query = req.GET.get('q')
    else:
        return do_404(req, message='No query')
    def default_app_handler(app, query, req):
        """
        Search through every model in model_dict with query
        """
        results = {}
        for model in app.get_models():
            if getattr(model._meta, 'sv_searchable_fields', None) is not None:
                m_query = Q()
                for field in model._meta.sv_searchable_fields:
                    m_query = m_query | Q(**{
                        '%s__icontains' % field: query
                    })
                matching = model.objects.filter(m_query)
                if matching.exists():
                    results[model._meta.verbose_name] = matching
        if results != {}:
            return mark_safe(render_to_string('common/search_section.html', {
                'results': results,
                'request': req,
                }))

    ## Resulsts is a key:value dict of app.verbose_name to rendered html
    results = {}
    for app in apps.get_app_configs():
        app_result = None
        if getattr(app, 'custom_search', None):
            app_result = app.custom_search(query, req)
        else:
            app_result = default_app_handler(app, query, req)
        if app_result is not None:
            results[app.verbose_name] = app_result

    return render(req, 'common/search.html', {'results': results})

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
