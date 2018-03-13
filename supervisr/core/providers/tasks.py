"""supervisr core provider tasks"""
from logging import getLogger

from supervisr.core.celery import CELERY_APP
from supervisr.core.providers.exceptions import SupervisrProviderException
from supervisr.core.providers.objects import ProviderObject

LOGGER = getLogger(__name__)


@CELERY_APP.task(bind=True, max_retries=10)
def provider_do_save(self, provider_object: ProviderObject):
    """Run the actual saving procedure and keep trying on failure"""
    try:
        provider_object.save()
        LOGGER.debug("Saved instance.")
    except SupervisrProviderException:
        self.retry(args=[provider_object], countdown=2 ** self.request.retries)


@CELERY_APP.task(bind=True, max_retries=10)
def provider_do_delete(self, provider_object: ProviderObject):
    """Run the actual deletion procedure and keep trying on failure"""
    try:
        provider_object.delete()
        LOGGER.debug("Deleted instance.")
    except SupervisrProviderException:
        self.retry(args=[provider_object], countdown=2 ** self.request.retries)
