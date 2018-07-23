"""supervisr core provider multiplexer"""
from logging import getLogger
from typing import List

from django.db.models import Model

from supervisr.core.celery import CELERY_APP
from supervisr.core.providers.base import BaseProvider
from supervisr.core.providers.objects import ProviderObjectTranslator
from supervisr.core.utils import class_to_path

LOGGER = getLogger(__name__)


class ProviderMultiplexer(object):
    """Multiplex signals to all relevent providers"""

    def get_translator(self, instance: Model, root_provider: BaseProvider, iteration=0)\
            -> ProviderObjectTranslator:
        """Recursively walk through providers.
        Limited to 100 iterations to prevent infinite loops"""
        sub_provider = root_provider.get_provider(type(instance))
        if sub_provider:
            if iteration >= 100:
                LOGGER.debug("Provider walk canceled, 100 iterations reached")
            sub_provider_instance = sub_provider(root_provider.credentials)
            LOGGER.debug("Redirected from %r to %r", root_provider, sub_provider_instance)
            return self.get_translator(instance, sub_provider_instance, iteration=iteration + 1)
        translator = root_provider.get_translator(type(instance))
        if translator:
            return translator(provider_instance=root_provider)
        return None

    def on_model_saved(self, invoker: 'User', instance: Model, providers: List['ProviderInstance']):
        """Notify providers that model was saved so translation can start"""
        from supervisr.core.providers.tasks import provider_do_save
        LOGGER.debug("instance %r, providers %r", instance, providers)
        for provider in providers:
            args = (provider.pk, class_to_path(instance.__class__), instance.pk)
            queue = provider.provider.__class__.__name__
            CELERY_APP.control.add_consumer(queue)
            invoker.task_apply_async(provider_do_save, *args, celery_kwargs={
                'queue': queue
            }, users=provider.users.all())
            LOGGER.debug("Fired task provider_do_save")

    def on_model_deleted(self, invoker: 'User', instance: Model,
                         providers: List['ProviderInstance']):
        """Notify providers that model is about to be deleted"""
        from supervisr.core.providers.tasks import provider_do_delete
        LOGGER.debug("instance %r, providers %r", instance, providers)
        for provider in providers:
            args = (provider.pk, class_to_path(instance.__class__), instance.pk)
            queue = provider.provider.__class__.__name__
            CELERY_APP.control.add_consumer(queue)
            invoker.task_apply_async(provider_do_delete, *args, celery_kwargs={
                'queue': queue
            }, users=provider.users.all())
            LOGGER.debug("Fired task provider_do_delete")
