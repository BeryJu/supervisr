"""
Supervisr Core Domain Provider
"""

from .base import BaseProvider


class DomainProvider(BaseProvider):
    """
    Base Provider for all domains
    """

    def register(self, domain, **kwargs):
        """
        Register method, used to register a new domain.
        """
        pass

    def check_available(self, domain):
        """
        Check if a domain is already in use
        """
        pass

    def check_expiry(self, domain):
        """
        Check when a domain is expiring
        """
        pass

    def import_domains(self):
        """
        Import domains from provider
        """
        pass
