"""supervisr mod provider libcloud Zone Translator"""
from logging import getLogger
from typing import Generator

from libcloud.common.exceptions import BaseHTTPError
from libcloud.dns.types import ZoneAlreadyExistsError

from supervisr.core.providers.exceptions import ProviderRetryException
from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator,
                                              ProviderResult)
from supervisr.dns.models import Zone

TYPE_FIXES = {
    'vultr': {
        'serverip': '127.0.0.1',
    }
}
LOGGER = getLogger(__name__)

class LCloudZoneObject(ProviderObject):
    """LCloud intermediate Zone object"""

    lc_zone = None
    type = None
    ttl = None

    def save(self, **kwargs) -> ProviderResult:
        """Save this instance"""
        try:
            if 'created' in kwargs:
                extra = TYPE_FIXES.get(self.translator.provider_instance.driver.type, {})
                self.translator.provider_instance.driver.create_zone(
                    domain=self.name,
                    type=self.type,
                    ttl=self.ttl,
                    extra=extra
                )
            else:
                LOGGER.warning("libcloud Zone updating not implemented")
                return ProviderResult.NOT_IMPLEMENTED
        except NotImplementedError:
            return ProviderResult.NOT_IMPLEMENTED
        except ZoneAlreadyExistsError:
            return ProviderResult.EXISTS_ALREADY
        except BaseHTTPError as exc:
            raise ProviderRetryException from exc
        return ProviderResult.SUCCESS

    def delete(self, **kwargs) -> ProviderResult:
        """Delete this instance"""
        try:
            _zone = None
            for zone in self.translator.provider_instance.driver.list_zones():
                if zone.domain == '%s.' % self.name:
                    _zone = zone
            if _zone:
                if self.translator.provider_instance.driver.delete_zone(_zone):
                    return ProviderResult.SUCCESS
            return ProviderResult.OTHER_ERROR
        except BaseHTTPError as exc:
            raise ProviderRetryException from exc


class LCloudZoneTranslator(ProviderObjectTranslator[Zone]):
    """PowerDNS Zone Translator"""

    def to_external(self, internal: Zone) -> Generator[LCloudZoneObject, None, None]:
        """Convert Zone to Domain"""
        yield LCloudZoneObject(
            translator=self,
            id=internal.pk,
            name=internal.domain.domain_name,
            type='master',
            ttl=86400,
        )
