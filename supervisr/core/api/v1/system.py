"""
Supervisr Core APIv1
"""

from django.core.cache import cache

from supervisr.core.api.utils import api_response
from supervisr.core.signals import SIG_GET_MOD_HEALTH
from supervisr.core.utils import check_db_connection


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
        'database': check_db_connection(),
        'cache': _cache_status(),
    }
    results = SIG_GET_MOD_HEALTH.send(sender=health)
    for handler, mod_info in results:
        # Get the handler's root module
        data[handler.__module__] = mod_info
    return api_response(req, data)
