"""supervisr core provider multiplexer"""
from logging import getLogger
from typing import List

from django.db.models import Model

from supervisr.core.models import ProviderInstance
from supervisr.core.providers.base import BaseProvider
from supervisr.core.providers.exceptions import SupervisrProviderException
from supervisr.core.providers.objects import ProviderObjectTranslator

LOGGER = getLogger(__name__)


class ProviderMultiplexer(object):
    """Multiplex signals to all relevent providers"""

    def _get_translators(self, instance: Model, providers: List[ProviderInstance]) \
            -> List[ProviderObjectTranslator]:
        """Get list of translators which should be run for instance.
        This also detects loops of providers."""
        translators = []
        for provider_instance in providers:
            translator = self._get_translator(instance, provider_instance.provider)
            if translator:
                translators.append(translator)
                LOGGER.debug("Got %r as translator for %r from provider %r", translator,
                             instance, provider_instance.provider)
        return translators

    def _get_translator(self, instance: Model, root_provider: BaseProvider, iteration=0)\
            -> ProviderObjectTranslator:
        """Recursively walk through providers.
        Limited to 100 iterations to prevent infinite loops"""
        sub_provider = root_provider.get_provider(type(instance))
        if sub_provider:
            if iteration >= 100:
                LOGGER.debug("Provider walk canceled, 100 iterations reached")
            sub_provider_instance = sub_provider(root_provider.credentials)
            LOGGER.debug("Redirected from %r to %r", root_provider, sub_provider_instance)
            return self._get_translator(instance, sub_provider_instance, iteration=iteration + 1)
        translator = root_provider.get_translator(type(instance))
        if translator:
            return translator(provider_instance=root_provider)
        return None

    def on_model_saved(self, instance: Model, providers: List[ProviderInstance]):
        """Notify providers that model was saved so translation can start"""
        LOGGER.debug("instance %r, providers %r", instance, providers)
        for translator in self._get_translators(instance, providers):
            provider_object = translator.to_external(instance)
            try:
                provider_object.save()
            except SupervisrProviderException as exc:
                LOGGER.warning("Provider Exception: %r", exc)
            LOGGER.debug("Saved instance.")

    def on_model_deleted(self, instance: Model, providers: List[ProviderInstance]):
        """Notify providers that model is about to be deleted"""
        LOGGER.debug("instance %r, providers %r", instance, providers)
        for translator in self._get_translators(instance, providers):
            provider_object = translator.to_external(instance)
            try:
                provider_object.delete()
            except SupervisrProviderException as exc:
                LOGGER.warning("Provider Exception: %r", exc)
            LOGGER.debug("Deleted instance.")
