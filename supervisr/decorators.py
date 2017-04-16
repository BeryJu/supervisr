"""
supervisr view decorators
"""

import time

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode


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

        if 'supervisr_require_reauth_done' in req.session and \
            req.session['supervisr_require_reauth_done'] > (now + 300):
            del req.session['supervisr_require_reauth_done']

        if 'supervisr_require_reauth_done' not in req.session:
            return redirect(reverse('account-reauth')+'?'+
                            urlencode({'next': req.path}))

        if 'supervisr_require_reauth_done' in req.session and \
            req.session['supervisr_require_reauth_done'] <= (now + 300):
            return view_function(*args, **kwargs)

    wrap.__doc__ = view_function.__doc__
    wrap.__name__ = view_function.__name__
    return wrap
