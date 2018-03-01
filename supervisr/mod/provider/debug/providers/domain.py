"""
Supervisr Debug Domain Provider
"""

from supervisr.core.providers.domain import DomainProvider
from supervisr.mod.provider.debug.providers.marshalls.core_domain import \
    DebugDomainMarshall


class DebugDomainProvider(DomainProvider):
    """
    Debug provider
    """
    parent = None
    domain_marshall = DebugDomainMarshall

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
