"""supervisr mod provider libcloud Zone Translator"""
from logging import getLogger
from typing import List

from libcloud.common.exceptions import BaseHTTPError
from libcloud.dns.types import ZoneAlreadyExistsError

from supervisr.core.providers.exceptions import (ProviderObjectNotFoundException,
                                                 ProviderRetryException)
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

    def save(self, created: bool):
        """Save this instance"""
        try:
            if created:
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

    def delete(self):
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

    def to_external(self, internal: Zone) -> LCloudZoneObject:
        """Convert Zone to Domain"""
        return LCloudZoneObject(
            translator=self,
            id=internal.pk,
            name=internal.domain.domain_name,
            type='master',
            ttl=86400,
        )

    def query_external(self, **kwargs) -> List[LCloudZoneObject]:
        """Query Domain"""
        raise NotImplementedError

    def to_internal(self, query_result: LCloudZoneObject) -> Zone:
        """Convert query_result to Zone"""
        zones = Zone.objects.filter(domain__domain_name=query_result.name)
        if not zones.exists():
            raise ProviderObjectNotFoundException()
        return zones.first()
