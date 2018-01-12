"""
supervisr mod contrib bacula decorators
"""

from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from supervisr.core.utils import check_db_connection


def check_bacula_db(view_function):
    """
    Decorator to check bacula DB before running
    """
    def wrap(*args, **kwargs):
        """
        Decorator to check bacula DB before running
        """
        request = args[0] if args else None
        if not check_db_connection('bacula') and request:
            return render(request, 'common/error.html', {
                'code': 500,
                'exc_message': _('An error occured while trying to connect to the Bacula database.')
                })
        return view_function(*args, **kwargs)

    wrap.__doc__ = view_function.__doc__
    wrap.__name__ = view_function.__name__
    return wrap
