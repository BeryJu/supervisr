"""supervisr view decorators"""

import base64
import warnings
from contextlib import contextmanager
from datetime import datetime
from time import time as timestamp

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.core.exceptions import AppRegistryNotReady, ObjectDoesNotExist
from django.db.utils import InternalError, OperationalError, ProgrammingError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.functional import wraps
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from supervisr.core.utils import get_apps
from supervisr.core.utils.statistics import StatisticType, set_statistic

RE_AUTH_KEY = getattr(settings, 'RE_AUTH_KEY', 'supervisr_require_re_auth_done')
RE_AUTH_MARGAIN = getattr(settings, 'RE_AUTH_MARGAIN', 300)


def anonymous_required(view_function):
    """Decorator to only allow a view for anonymous users"""

    @wraps(view_function)
    def wrap(*args, **kwargs):
        """Check if request's user is authenticated and route back to index"""

        req = args[0] if args else None
        if req and req.user is not None and req.user.is_authenticated:
            return redirect(reverse('common-index'))
        return view_function(*args, **kwargs)
    return wrap


def database_catchall(default):
    """Decorator to catch all possible Database Errors and return a default value"""

    def outer_wrapper(method):
        """Decorator to catch all possible Database Errors and return a default value"""

        @wraps(method)
        def catchall(*args, **kwargs):
            """Decorator to catch all possible Database Errors and return a default value"""
            try:
                return method(*args, **kwargs)
            except (AppRegistryNotReady, ObjectDoesNotExist,
                    OperationalError, InternalError, ProgrammingError):
                # Handle Postgres transaction revert
                if 'postgresql' in settings.DATABASES['default']['ENGINE']:
                    from django.db import connection
                    # pylint: disable=protected-access
                    connection._rollback()
                return default
            else:
                return default
        return catchall
    return outer_wrapper



def require_setting(path, value, message=_('This function has been administratively disabled.')):
    """Check if setting under *key* has value of *value*

    Args:
        path: Complete path to the setting, i.e. supervisr.core/banner:enabled
        value: The value which Setting should have.
        message: The message which should be shown

    Returns:
        Inner-wrapper
    """

    def outer_wrap(view_func):
        """Check if setting under *key* has value of *value*"""

        @wraps(view_func)
        def wrap(request, *args, **kwargs):
            """Check if setting under *key* has value of *value*"""
            from supervisr.core.models import Setting

            namespace, key = path.split('/')
            setting = Setting.objects.filter(namespace=namespace, key=key)

            # pylint: disable=unidiomatic-typecheck
            if setting.exists() and \
                    (type(value) == bool and setting.first().value_bool != value or
                     type(value) != bool and setting.first().value != value):
                # Only show error if setting exists and doesnt match value
                return render(request, 'common/error.html', {'message': message})

            return view_func(request, *args, **kwargs)
        return wrap
    return outer_wrap


def ifapp(app_name):
    """Only executes ifapp_func if app_name is installed"""

    def get_app_labels():
        """Cache all installed apps and return the list"""

        cache_key = 'ifapp_apps'
        if not cache.get(cache_key):
            # Make a list of all short names for all apps
            app_cache = []
            for app in get_apps():
                app_cache.append(app.label)
            cache.set(cache_key, app_cache, 1000)
            return app_cache
        return cache.get(cache_key)  # pragma: no cover

    app_cache = get_app_labels()

    def outer_wrap(ifapp_func):
        """Only executes ifapp_func if app_name is installed"""

        @wraps(ifapp_func)
        def wrap(*args, **kwargs):
            """Only executes ifapp_func if app_name is installed"""
            if app_name in app_cache or app_name == 'supervisr_core':
                return ifapp_func(*args, **kwargs)
            return False
        return wrap
    return outer_wrap


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return new_func


def view_or_basicauth(view, request, test_func, realm, *args, **kwargs):
    """This is a helper function used by both 'logged_in_or_basicauth' and
    'has_perm_or_basicauth' that does the nitty of determining if they
    are already logged in or if they have provided proper http-authorization
    and returning the view if all goes well, otherwise responding with a 401."""
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
                email, passwd = base64.b64decode(auth[1]).decode('utf-8').split(':')
                user = authenticate(email=email, password=passwd, request=request)
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
        """Outter wrapper"""
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            """Inner wrapper"""
            return view_or_basicauth(func, request,
                                     lambda u: u.is_authenticated,
                                     realm, *args, **kwargs)
        return wrapper
    return view_decorator
