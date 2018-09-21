"""supervisr dns provider compatibility"""
from copy import deepcopy
from itertools import chain
from logging import getLogger
from typing import Generator, List, Union

from supervisr.core.decorators import time
from supervisr.core.providers.base import BaseProvider
from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator)
from supervisr.dns.models import BaseRecord, DataRecord, SetRecord

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

    def __str__(self):
        return "%s (type=%s, content=%s)" % (self.name, self.type, self.content)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class CompatDNSTranslator(ProviderObjectTranslator):
    """Compatibility wrapper for Record/Resource/ResourceSet
    Instances to translate calls to Record"""

    @time('dns.provider.compat.CompatDNSTranslator.build_compat_records')
    def build_compat_records(self, record: BaseRecord) -> List[CompatDNSRecord]:
        """Build CompatDNSRecord from DB Models. Resource Membership in record is not checked.

        Args:
            record (Record): Record instance to use.

        Returns:
            Generator[CompatDNSRecord]: Generator of newly created CompatDNSRecord instance
        """

        def walk_zones_backwards(base_record):
            """Recursively walk zones reverse to collect all zones"""
            zones = list(base_record.zone_set.all())
            if isinstance(base_record, DataRecord):
                for parent_sub in base_record.set.all():
                    if parent_sub.enabled:
                        zones += walk_zones_backwards(parent_sub.cast())
            return zones

        def walk_records(record, name_parts=None):
            """Recursively create CompatDNSRecord instances"""
            if name_parts is None:
                name_parts = []
            compat_records = []
            if isinstance(record, DataRecord) and record.enabled:
                # Just a single record, no recursion needed
                compat_records.append(CompatDNSRecord(
                    type=record.type,
                    content=record.content,
                    ttl=record.ttl,
                    priority=record.priority,
                    enabled=record.enabled,
                    name_parts=name_parts + [record.name]
                ))
            elif isinstance(record, SetRecord) and record.enabled:
                # Check for record.append_name
                name_parts.append(record.name)
                for sub_record in record.records.all():
                    compat_records += walk_records(sub_record.cast(), name_parts=name_parts)
            return compat_records

        # First get a list of all zones, which is gonna be used later to update the CompatDNSRecord
        # instances
        zones = walk_zones_backwards(record.cast())
        # Get a complete list of all records to be created
        compat_records = walk_records(record.cast())
        all_records = []
        for zone in zones:
            for compat_record in compat_records:
                # Create a copy of the record since it's going to be used
                # multiple times
                compat_record = deepcopy(compat_record)
                # Set Domain
                compat_record.domain = str(zone)
                # Reverse all name parts since we reverse-walked them
                compat_record.name_parts.reverse()
                # If there is an @ in the names, truncate parts until that and remove @ aswell
                if '@' in compat_record.name_parts:
                    at_index = compat_record.name_parts.index('@') - 1
                    del compat_record.name_parts[at_index:]
                # Append domain so we can use join for everything
                compat_record.name_parts.append(compat_record.domain)
                # Join them with . and add domain to end
                compat_record.name = '.'.join(compat_record.name_parts)
                all_records.append(compat_record)
        return all_records

    def to_external(self, internal: BaseRecord) -> Generator[ProviderObject, None, None]:
        record_translator = self.provider_instance.get_translator(CompatDNSRecord)
        translator_instance = record_translator(provider_instance=self.provider_instance)
        compat_records = self.build_compat_records(internal)
        generators = []
        for compat_record in compat_records:
            generators.append(translator_instance.to_external(compat_record))
        LOGGER.debug("Translated Resource update to Record Update")
        return chain(*generators)


class CompatDNSProvider(BaseProvider):
    """Compatibility wrapper to emulate classic DNS Behavior"""

    def get_translator(self, data_type) -> ProviderObjectTranslator:
        """Get translator for type. If none available return None"""
        if data_type in [DataRecord, SetRecord, BaseRecord]:
            return CompatDNSTranslator
        return super().get_translator(data_type)

    def check_credentials(self, credentials=None) -> bool:
        raise NotImplementedError()

    def check_status(self) -> Union[bool, str]:
        raise NotImplementedError()
