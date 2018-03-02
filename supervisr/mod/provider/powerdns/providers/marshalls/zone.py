"""supervisr mod provider powerdns Zone Marshall"""
from typing import List

from supervisr.core.models import Domain
from supervisr.core.providers.objects import ProviderObjectMarshall
from supervisr.dns.models import Zone
from supervisr.mod.provider.powerdns.models import Domain as PDNSDomain


class PowerDNSZoneMarshall(ProviderObjectMarshall[Zone]):
    """PowerDNS Zone Marshall"""

    def create(self, instance: Zone) -> bool:
        """Create instance of Object with **kwargs"""
        PDNSDomain.objects.create(
            name=instance.domain.domain_name
        )

    def has(self, **filters) -> bool:
        """Check if Object matching from key-value filters from **filters exists"""
        raise NotImplementedError()

    def read(self, **filters) -> List[Zone]:
        """Return List of Object matching key-value filters from **filters"""
        pdns_domains = Domain.objects.filter(**filters)
        converted = []
        for domain in pdns_domains:
            core_domains = Domain.objects.filter(domain_name=domain.name)
            core_domain = None
            if core_domains.exists():
                core_domain = core_domains.first()
            else:
                core_domain = Domain(domain_name=domain.name)
            converted.append(Zone(domain=core_domain))

    # pylint: disable=unused-argument
    def update(self, instance: Zone) -> bool:
        """Write updated instance"""
        # pdns_instance = Domain.objects.filter(name=instance.domain.domain_name)
        # There is only one field being translated so we can't update
        return True

    def delete(self, instance: Zone) -> bool:
        """Delete instance"""
        return Domain.objects.filter(name=instance.domain.domain_name).delete()
