"""Supervisr Core APIv1"""
import celery

from django.core.cache import cache

from supervisr.core.api.base import API
from supervisr.core.signals import get_module_health
from supervisr.core.utils import check_db_connection
from supervisr.core.exceptions import UnauthorizedException


class SystemAPI(API):
    """System API"""

    ALLOWED_VERBS = {
        'GET': ['health', 'workers']
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

    def workers(self, request, data):
        """Get celery worker list"""
        if not request.user.is_superuser:
            raise UnauthorizedException()
        celery_dict = celery.current_app.control.inspect().ping()
        workers = []
        for worker_name, worker_status in celery_dict.items():
            workers.append({
                'name': worker_name,
                'status': worker_status.get('ok')
            })
        return workers
