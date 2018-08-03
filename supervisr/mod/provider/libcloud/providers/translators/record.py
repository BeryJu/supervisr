"""supervisr mod provider libcloud Record Translator"""
from typing import List

from libcloud.common.exceptions import BaseHTTPError
from libcloud.dns.types import RecordAlreadyExistsError

from supervisr.core.providers.exceptions import (ProviderObjectNotFoundException,
                                                 ProviderRetryException)
from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator,
                                              ProviderrResult)
from supervisr.dns.models import Record


class LCloudRecordObject(ProviderObject):
    """LCloud intermediate Record object"""

    lc_zone = None
    type = None
    ttl = None

    def save(self):
        """Save this instance"""
        try:
            print('test')
            # return self.translator.provider_instance.driver.create_record(
            #     domain=self.name,
            #     type=self.type,
            #     ttl=self.ttl,
            #     extra=extra
            # )
        except NotImplementedError:
            return ProviderrResult.NOT_IMPLEMENTED
        except RecordAlreadyExistsError:
            return ProviderrResult.EXISTS_ALREADY
        except BaseHTTPError as exc:
            raise ProviderRetryException from exc
        return ProviderrResult.SUCCESS

    def delete(self):
        """Delete this instance"""
        try:
            # _zone = None
            # for zone in self.translator.provider_instance.driver.list_zones():
            #     if zone.domain == self.name:
            #         _zone = zone
            # if self.translator.provider_instance.driver.delete_zone(_zone):
            #     return ProviderrResult.SUCCESS
            return ProviderrResult.OTHER_ERROR
        except BaseHTTPError as exc:
            raise ProviderRetryException from exc


class LCloudRecordTranslator(ProviderObjectTranslator[Record]):
    """PowerDNS Record Translator"""

    def to_external(self, internal: Record) -> LCloudRecordObject:
        """Convert Record to Domain"""
        return LCloudRecordObject(
            translator=self,
            id=internal.pk,
            name=internal.domain.domain_name,
            type='master',
            ttl=86400,
        )

    def query_external(self, **kwargs) -> List[LCloudRecordObject]:
        """Query Domain"""
        raise NotImplementedError

    def to_internal(self, query_result: LCloudRecordObject) -> Record:
        """Convert query_result to Record"""
        records = Record.objects.filter(domain__domain_name=query_result.name)
        if not records.exists():
            raise ProviderObjectNotFoundException()
        return records.first()
