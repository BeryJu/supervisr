"""
Supervisr Core Common Views
"""

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.utils import ConnectionDoesNotExist
from django.shortcuts import render
from django.utils.safestring import mark_safe

from supervisr.core.utils import do_404, render_to_string


@login_required
def search(req):
    """
    Searching of models and subapps
    """
    if 'q' in req.GET:
        query = req.GET.get('q')
    else:
        return do_404(req, message='No query')

    # def make_model_url(model):
    #     """
    #     Create a url for model
    #     """
    #     from django.core.urlresolvers import reverse
    #     if getattr(model._meta, 'sv_search_url', None) is not None:
    #         # if '%' in model._meta.sv_search_url:
    #         return model._meta.sv_search_url
    #     else:
    #         # default assumed formats are
    #         # 1: <app_label>:<model's verbose_name>
    #         # 2: <app_label>:<model's verbose_name>-view
    #         # 3: <app_label>:<model's verbose_name>-edit
    #         app_label = model._meta.app_label
    #         verbose_name = model._meta.verbose_name.replace(' ', '-')
    #         url_choices = ()

    def default_app_handler(app, query, req):
        """
        Search through every model in model_dict with query
        """
        results = {}
        for model in app.get_models():
            if getattr(model._meta, 'sv_search_fields', None) is not None:
                m_query = Q()
                for field in model._meta.sv_search_fields:
                    m_query = m_query | Q(**{
                        '%s__contains' % field: query
                    })
                matching = model.objects.filter(m_query)
                if matching.exists():
                    results[model._meta.verbose_name] = matching
        if results != {}:
            return mark_safe(render_to_string('search/search_section.html', {
                'results': results,
                'request': req,
                }))

    ## Resulsts is a key:value dict of app.verbose_name to rendered html
    results = {}
    for app in apps.get_app_configs():
        app_result = None
        try:
            # if getattr(app, 'custom_search', None):
            #     app_result = app.custom_search(query, req)
            # else:
            app_result = default_app_handler(app, query, req)
            if app_result is not None:
                results[app.verbose_name] = app_result
        except ConnectionDoesNotExist:
            pass

    return render(req, 'search/search.html', {'results': results})
