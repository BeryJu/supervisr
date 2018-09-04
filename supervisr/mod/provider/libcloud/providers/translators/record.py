"""supervisr mod provider libcloud Record Translator"""
from typing import Generator

from libcloud.common.exceptions import BaseHTTPError
from libcloud.dns.types import RecordAlreadyExistsError

from supervisr.core.providers.exceptions import ProviderRetryException
from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator,
                                              ProviderResult)
from supervisr.dns.models import Record


class LCloudRecordObject(ProviderObject):
    """LCloud intermediate Record object"""

    lc_zone = None
    type = None
    ttl = None

    def save(self, created: bool):
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
            return ProviderResult.NOT_IMPLEMENTED
        except RecordAlreadyExistsError:
            return ProviderResult.EXISTS_ALREADY
        except BaseHTTPError as exc:
            raise ProviderRetryException from exc
        return ProviderResult.SUCCESS

    def delete(self):
        """Delete this instance"""
        try:
            # _zone = None
            # for zone in self.translator.provider_instance.driver.list_zones():
            #     if zone.domain == self.name:
            #         _zone = zone
            # if self.translator.provider_instance.driver.delete_zone(_zone):
            #     return ProviderrResult.SUCCESS
            return ProviderResult.OTHER_ERROR
        except BaseHTTPError as exc:
            raise ProviderRetryException from exc


class LCloudRecordTranslator(ProviderObjectTranslator[Record]):
    """PowerDNS Record Translator"""

    def to_external(self, internal: Record) -> Generator[LCloudRecordObject, None, None]:
        """Convert Record to Domain"""
        yield LCloudRecordObject(
            translator=self,
            id=internal.pk,
            name=internal.domain.domain_name,
            type='master',
            ttl=86400,
        )
