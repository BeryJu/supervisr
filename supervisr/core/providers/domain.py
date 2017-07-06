"""
Supervisr Core Domain Provider
"""

from .base import BaseProvider


class DomainProvider(BaseProvider):
    """
    Base Provider for all domains
    """

    def check_credentials(self, credentials=None):
        """
        Check if Credentials is the correct class and try authentication.
        credentials might be none, in which case credentials from the constructor should be used.
        Should return False if check fails, otherwise True
        """
        raise NotImplementedError("This Method should be overwritten by subclasses")

    def check_status(self):
        """
        This is used to check if the provider is reachable
        Expected Return values:
         - True: Everything is ok
         - False: Error (show generic warning)
         - String: Error (show string)
        """
        raise NotImplementedError("This Method should be overwritten by subclasses")

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
