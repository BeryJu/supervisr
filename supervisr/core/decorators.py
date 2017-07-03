"""
supervisr view decorators
"""

import time

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode

REAUTH_KEY = getattr(settings, 'REAUTH_KEY', 'supervisr_require_reauth_done')
REAUTH_MARGIN = getattr(settings, 'REAUTH_MARGIN', 300)

def anonymous_required(view_function):
    """
    Decorator to only allow a view for anonymous users
    """
    def wrap(*args, **kwargs):
        """
        Check if request's user is authenticated and route back to index
        """
        req = args[0] if args else None
        if req and req.user is not None and req.user.is_authenticated():
            return redirect(reverse('common-index'))
        return view_function(*args, **kwargs)

    wrap.__doc__ = view_function.__doc__
    wrap.__name__ = view_function.__name__
    return wrap

def reauth_required(view_function):
    """
    Decorator to force a re-authentication before continuing
    """
    def wrap(*args, **kwargs):
        """
        check if user just authenticated or not
        """
        req = args[0] if args else None
        # Check if user is authenticated at all
        if not req or not req.user or not req.user.is_authenticated():
            return redirect(reverse('account-login'))

        now = time.time()

        if REAUTH_KEY in req.session and \
            req.session[REAUTH_KEY] < (now - REAUTH_MARGIN):
            # Timestamp in session but expired
            del req.session[REAUTH_KEY]

        if REAUTH_KEY not in req.session:
            # Timestamp not in session, force user to reauth
            return redirect(reverse('account-reauth')+'?'+
                            urlencode({'next': req.path}))

        if REAUTH_KEY in req.session and \
            req.session[REAUTH_KEY] >= (now - REAUTH_MARGIN) and \
            req.session[REAUTH_KEY] <= now:
            # Timestamp in session and valid
            return view_function(*args, **kwargs)

    wrap.__doc__ = view_function.__doc__
    wrap.__name__ = view_function.__name__
    return wrap

def ifapp(app_name):
    """
    Only executes ifapp_func if app_name is installed
    """
    cache_key = 'ifapp_apps'
    if not cache.get(cache_key):
        app_cache = []
        # Make a list of all short names for all apps
        if not app_cache:
            app_cache = []
            for app in settings.INSTALLED_APPS:
                if '.' in app:
                    parts = app.split('.')
                    if parts[0] == 'supervisr':
                        app_cache.append(parts[1])
                    else:
                        app_cache.append(parts[0])
                else:
                    app_cache.append(app)
    app_cache = cache.get(cache_key)

    def outer_wrap(ifapp_func):
        """
        Only executes ifapp_func if app_name is installed
        """
        def wrap(*args, **kwargs):
            """
            Only executes ifapp_func if app_name is installed
            """
            if app_name in app_cache:
                return ifapp_func(*args, **kwargs)
            return
        wrap.__doc__ = ifapp_func.__doc__
        wrap.__name__ = ifapp_func.__name__

        return wrap

    return outer_wrap
