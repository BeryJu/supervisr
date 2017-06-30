"""
Shib Processor
"""

from supervisr.mod.saml.idp.base import Processor
from supervisr.mod.saml.idp.xml_render import get_assertion_salesforce_xml


class ShibProcessor(Processor):
    """
    Shib-specific Processor
    """
    def _format_assertion(self):
        self._assertion_xml = get_assertion_salesforce_xml(self._assertion_params, signed=True)

    def _determine_audience(self):
        """
        Determines the _audience.
        """
        self._audience = "https://sp.testshib.org/shibboleth-sp"
