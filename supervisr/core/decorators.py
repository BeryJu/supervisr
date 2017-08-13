"""
supervisr view decorators
"""

import base64
import time

from django.apps import apps
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode

from supervisr.core.utils import get_apps

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
    def get_app_labels():
        """
        Cache all installed apps and return the list
        """
        cache_key = 'ifapp_apps'
        if not cache.get(cache_key):
            # Make a list of all short names for all apps
            app_cache = []
            for app in get_apps():
                try:
                    mod_new = '/'.join(app.split('.')[:-2])
                    config = apps.get_app_config(mod_new)
                    mod = mod_new
                except LookupError:
                    mod = app.split('.')[:-2][-1]
                    config = apps.get_app_config(mod)
                app_cache.append(config.label)
            cache.set(cache_key, app_cache, 1000)
            return app_cache
        return cache.get(cache_key)

    app_cache = get_app_labels()

    def outer_wrap(ifapp_func):
        """
        Only executes ifapp_func if app_name is installed
        """
        def wrap(*args, **kwargs):
            """
            Only executes ifapp_func if app_name is installed
            """
            if app_name in app_cache or app_name == 'core' or app_name == 'supervisr/core':
                return ifapp_func(*args, **kwargs)
            return
        wrap.__doc__ = ifapp_func.__doc__
        wrap.__name__ = ifapp_func.__name__

        return wrap

    return outer_wrap

def view_or_basicauth(view, request, test_func, realm="", *args, **kwargs):
    """
    This is a helper function used by both 'logged_in_or_basicauth' and
    'has_perm_or_basicauth' that does the nitty of determining if they
    are already logged in or if they have provided proper http-authorization
    and returning the view if all goes well, otherwise responding with a 401.
    """
    if test_func(request.user):
        # Already logged in, just return the view.
        #
        return view(request, *args, **kwargs)

    # They are not logged in. See if they provided login credentials
    #
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: We are only support basic authentication for now.
            #
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                user = authenticate(username=uname, password=passwd)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        return view(request, *args, **kwargs)

    # Either they did not provide an authorization header or
    # something in the authorization attempt failed. Send a 401
    # back to them to ask them to authenticate.
    #
    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return response

def logged_in_or_basicauth(realm=""):
    """
    A simple decorator that requires a user to be logged in. If they are not
    logged in the request is examined for a 'authorization' header.

    If the header is present it is tested for basic authentication and
    the user is logged in with the provided credentials.

    If the header is not present a http 401 is sent back to the
    requestor to provide credentials.

    The purpose of this is that in several django projects I have needed
    several specific views that need to support basic authentication, yet the
    web site as a whole used django's provided authentication.

    The uses for this are for urls that are access programmatically such as
    by rss feed readers, yet the view requires a user to be logged in. Many rss
    readers support supplying the authentication credentials via http basic
    auth (and they do NOT support a redirect to a form where they post a
    username/password.)

    Use is simple:

    @logged_in_or_basicauth
    def your_view:
        ...

    You can provide the name of the realm to ask for authentication within.
    """
    def view_decorator(func):
        """
        Outter wrapper
        """
        def wrapper(request, *args, **kwargs):
            """
            Inner wrapper
            """
            return view_or_basicauth(func, request,
                                     lambda u: u.is_authenticated(),
                                     realm, *args, **kwargs)
        return wrapper
    return view_decorator
