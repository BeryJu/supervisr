"""Supervisr Debug Provider"""

from logging import getLogger
from time import sleep
from typing import Generator

from django.utils.translation import ugettext_lazy as _

from supervisr.core.models import EmptyCredential, Setting
from supervisr.core.providers.base import BaseProvider, ProviderMetadata
from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator,
                                              ProviderResult)

LOGGER = getLogger(__name__)


class DebugObject(ProviderObject):
    """Debug intermediate object"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sleep_duration = Setting.get_int('sleep_duration')

    def save(self, **kwargs) -> ProviderResult:
        LOGGER.debug('Sleeping %ss', self.sleep_duration)
        sleep(self.sleep_duration)
        LOGGER.debug("Instance %s saved (kwargs=%r)", self.name, kwargs)
        return ProviderResult.SUCCESS

    def delete(self, **kwargs) -> ProviderResult:
        LOGGER.debug('Sleeping %ss', self.sleep_duration)
        sleep(self.sleep_duration)
        LOGGER.debug("Instance %s deleted (kwargs=%r)", self.name, kwargs)
        return ProviderResult.SUCCESS


class DebugTranslator(ProviderObjectTranslator):
    """Debug Zone Translator"""

    def to_external(self, internal) -> Generator[DebugObject, None, None]:
        """Convert to Debug """
        yield DebugObject(
            translator=self,
            internal=internal
        )


class DebugProvider(BaseProvider):
    """Debug Provider"""

    def check_credentials(self, credentials: EmptyCredential = None):
        """Check if credentials are instance of BaseCredential"""
        return True

    def get_translator(self, data_type) -> ProviderObjectTranslator:
        return DebugTranslator

    def get_provider(self, data_type) -> BaseProvider:
        return None

    def check_status(self):
        """Check connection status"""
        return True

    class Meta(ProviderMetadata):
        """Debug core provider meta"""

        ui_description = _('Provides absolutely nothing.')
        ui_name = _('Debug')
        capabilities = ['dns', 'mail', 'domain']
