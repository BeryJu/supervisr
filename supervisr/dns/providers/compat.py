"""supervisr dns provider compatibility"""
from itertools import chain
from logging import getLogger
from typing import Generator, Union

from supervisr.core.providers.base import BaseProvider
from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator)
from supervisr.dns.models import Record, Resource, ResourceSet

LOGGER = getLogger(__name__)

class CompatDNSRecord:
    """Compatibility Class used to store DNS data in a more traditional way"""

    domain = ''
    name = ''
    type = ''
    content = ''
    ttl = 3600
    priority = 0
    enabled = True

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

class CompatDNSTranslator(ProviderObjectTranslator):
    """Compatibility wrapper for Record/Resource/ResourceSet
    Instances to translate calls to Record"""

    def __build_compat_record(self, resource: Resource, record: Record) -> CompatDNSRecord:
        """Build CompatDNSRecord from DB Models. Resource Membership in record is not checked.

        Args:
            resource (Resource): Resource instance to use.
            record (Record): Record instance to use.

        Returns:
            CompatDNSRecord: Newly created CompatDNSRecord instance
        """
        return CompatDNSRecord(
            domain=record.record_zone.domain.domain_name,
            name=record.fqdn,
            type=resource.type,
            content=resource.content,
            ttl=resource.ttl,
            priority=resource.priority,
            enabled=resource.enabled,
        )

    def to_external(self, internal: Union[Record, Resource, ResourceSet]
                   ) -> Generator[ProviderObject, None, None]:
        record_translator = self.provider_instance.get_translator(CompatDNSRecord)
        translator_instance = record_translator(provider_instance=self.provider_instance)
        compat_records = []
        generators = []
        if isinstance(internal, Record):
            LOGGER.debug("COMPAT Resource")
            for resource in internal.resource_set.resource.all():
                compat_records.append(self.__build_compat_record(resource, internal))
        elif isinstance(internal, ResourceSet):
            LOGGER.debug("COMPAT ResourceSet")
            for record in internal.record_set.all():
                for resource in record.resource_set.resource.all():
                    compat_records.append(self.__build_compat_record(resource, record))
        elif isinstance(internal, Resource):
            LOGGER.debug("COMPAT Record")
            for resource_set in internal.resourceset_set.all():
                for record in resource_set.record_set.all():
                    for resource in record.resource_set.resource.all():
                        compat_records.append(self.__build_compat_record(resource, record))
        for compat_record in compat_records:
            generators.append(translator_instance.to_external(compat_record))
        LOGGER.debug("Translated Resource update to Record Update")
        return chain(*generators)


class CompatDNSProvider(BaseProvider):
    """Compatibility wrapper to emulate classic DNS Behavior"""

    def get_translator(self, data_type) -> ProviderObjectTranslator:
        """Get translator for type. If none available return None"""
        if data_type in [Resource, ResourceSet, Record]:
            return CompatDNSTranslator
        return super().get_translator(data_type)

    def check_credentials(self, credentials=None) -> bool:
        raise NotImplementedError()

    def check_status(self) -> Union[bool, str]:
        raise NotImplementedError()
