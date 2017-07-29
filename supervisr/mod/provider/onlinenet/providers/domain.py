"""
Supervisr OnlineNet Domain Provider
"""

import logging

from supervisr.core.providers.domain import DomainProvider

LOGGER = logging.getLogger(__name__)

# pylint: disable=too-few-public-methods
class OnlineNetDomainProvider(DomainProvider):
    """
    OnlineNet provider
    """
    parent = None

    def register(self, domain, **kwargs):
        """
        Register method, used to register a new domain.
        """
        LOGGER.info("register: %s %s", domain, kwargs)
        pass

    def check_available(self, domain):
        """
        Check if a domain is already in use
        """
        LOGGER.info("check_available: %s", domain)
        return True

    def check_expiry(self, domain):
        """
        Check when a domain is expiring
        """
        LOGGER.info("check_expiry: %s", domain)
        pass

    def import_domains(self):
        """
        Import domains from provider
        """
        LOGGER.info("import_domains:")
        pass
