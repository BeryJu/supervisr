"""Supervisr Core APIv1"""

from django.core.cache import cache

from supervisr.core.api.base import API
from supervisr.core.signals import get_module_health
from supervisr.core.utils import check_db_connection


class SystemAPI(API):
    """System API"""

    ALLOWED_VERBS = {
        'GET': ['health']
    }

    @staticmethod
    def init_user_filter(user):
        """This method is used to check if the user has access"""
        return True

    def _cache_status(self):
        """Check cache status by setting and getting a value"""
        cache.set('djangohealtcheck_test', 'itworks', 1)
        if not cache.get("djangohealtcheck_test") == "itworks":
            return False
        return True

    def health(self, request, data):
        """Return Status"""
        data = {
            'database': check_db_connection(),
            'cache': self._cache_status(),
        }
        results = get_module_health.send(sender=self.health)
        for handler, mod_info in results:
            # Get the handler's root module
            data[handler.__module__] = mod_info
        return data
