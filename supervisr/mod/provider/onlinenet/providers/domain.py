"""
Supervisr OnlineNet Domain Provider
"""

import logging

from supervisr.core.providers.domain import DomainProvider

LOGGER = logging.getLogger(__name__)


class OnlineNetDomainProvider(DomainProvider):
    """
    OnlineNet provider
    """
    parent = None

    def check_credentials(self, credentials=None):
        """
        Check if Credentials is the correct class and try authentication.
        credentials might be none, in which case credentials from the constructor should be used.
        Should return False if check fails, otherwise True
        """
        return self.parent.check_credentials(credentials)

    def check_status(self):
        """
        This is used to check if the provider is reachable
        Expected Return values:
         - True: Everything is ok
         - False: Error (show generic warning)
         - String: Error (show string)
        """
        return self.parent.check_status()

    def register(self, domain, **kwargs):
        """
        Register method, used to register a new domain.
        """
        LOGGER.info("register: %s %s", domain, kwargs)

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

    def import_domains(self):
        """
        Import domains from provider
        """
        LOGGER.info("import_domains:")
