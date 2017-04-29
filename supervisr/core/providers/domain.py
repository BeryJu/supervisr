"""
Supervisr Core Domain Provider
"""

from .BaseProvider import BaseProvider

class DomainProvider(BaseProvider):
    """
    Base Provider for all domains
    """

    def register(self, domain):
        pass

    def check_available(self, domain):
        pass

    def check_expiry(self, domain):
        pass

    def import_domains(self):
        pass
