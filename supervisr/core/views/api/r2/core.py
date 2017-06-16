"""
Supervisr Core APIv2
"""

from django.core.cache import cache
from django.db import connections
from django.db.utils import OperationalError

from supervisr.core.signals import SIG_GET_MOD_HEALTH
from supervisr.core.views.api.utils import api_response


def _db_status():
    db_conn = connections['default']
    try:
        db_conn.cursor()
    except OperationalError:
        return False
    else:
        return True

def _cache_status():
    cache.set('djangohealtcheck_test', 'itworks', 1)
    if not cache.get("djangohealtcheck_test") == "itworks":
        return False
    return True

def health(req):
    """
    Return oursevles as json
    """
    data = {
        'database': _db_status(),
        'cache': _cache_status(),
    }
    results = SIG_GET_MOD_HEALTH.send(sender=health)
    for handler, mod_info in results:
        # Get the handler's root module
        data[handler.__module__] = mod_info
    return api_response(req, data)