"""supervisr mod provider powerdns Zone Translator"""
from typing import List

from django.db.utils import OperationalError

from supervisr.core.providers.exceptions import (ProviderObjectNotFoundException,
                                                 SupervisrProviderException)
from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator)
from supervisr.dns.models import Zone
from supervisr.mod.provider.nix_dns.models import Domain


class PowerDNSZoneObject(ProviderObject):
    """PowerDNS intermediate Zone object"""

    account = None

    def save(self):
        """Save this instance"""
        try:
            existing = Domain.objects.filter(name=self.name, pk=self.id)
            if existing.exists():
                # Domain has been updated
                assert len(existing) == 1
                domain = existing.first()
                domain.name = self.name
                domain.account = self.account
                domain.save()
                return False
            # pylint: disable=invalid-name
            self.id = Domain.objects.create(
                name=self.name,
                account=self.account,
            ).id
            return True
        except OperationalError as exc:
            raise SupervisrProviderException from exc

    def delete(self):
        """Delete this instance"""
        try:
            existing = Domain.objects.filter(name=self.name, pk=self.id)
            if not existing.exists():
                raise ProviderObjectNotFoundException()
            assert len(existing) == 1
            existing.first().delete()
        except OperationalError as exc:
            raise SupervisrProviderException from exc


class PowerDNSZoneTranslator(ProviderObjectTranslator[Zone]):
    """PowerDNS Zone Translator"""

    def to_external(self, internal: Zone) -> PowerDNSZoneObject:
        """Convert Zone to Domain"""
        return PowerDNSZoneObject(
            translator=self,
            id=internal.pk,
            name=internal.domain.domain_name
        )

    def query_external(self, **kwargs) -> List[PowerDNSZoneObject]:
        """Query Domain"""
        results = []
        domains = Domain.objects.filter(**kwargs)
        for domain in domains:
            result_obj = PowerDNSZoneObject(self)
            result_obj.id = domain.pk
            result_obj.name = domain.name
            results.append(result_obj)
        return results

    def to_internal(self, query_result: PowerDNSZoneObject) -> Zone:
        """Convert query_result to Zone"""
        matching = Domain.objects.filter(pk=query_result.id)
        if not matching.exists() or len(matching) > 1:
            raise ProviderObjectNotFoundException()
        zones = Zone.objects.filter(domain__domain_name=query_result.name)
        if not zones.exists():
            raise ProviderObjectNotFoundException()
        assert len(zones) == 1
        return zones.first()
