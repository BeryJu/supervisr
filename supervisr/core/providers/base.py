"""Supervisr Core Generic Provider"""
from typing import Type, Union

from django.utils.translation import ugettext_lazy as _

from supervisr.core.providers.objects import ProviderObjectTranslator
from supervisr.core.utils import class_to_path


class ProviderMetadata(object):
    """This is a class to store metadata like ui_name etc about a provider"""

    selectable = True
    ui_name = "ui_name hasn't been overridden"
    ui_description = "ui_description hasn't been overridden"
    provider = None
    capabilities = []

    def __init__(self, provider):
        self.provider = provider
        self.ui_name = _(self.ui_name)
        self.ui_description = _(self.ui_description)

    def get_capabilities(self):
        """Return all subproviders this provider has"""
        return self.capabilities

    def get_author(self):
        """Return Provider Author"""
        return 'BeryJu.org'

class BaseProvider(object):
    """Generic Interface as base for GenericManagedProvider and GenericUserProvider"""

    credentials = None
    _meta = None

    def __init__(self, credentials):
        self._meta = self.Meta(self)
        if credentials:
            self.credentials = credentials.cast()

    @property
    def dotted_path(self):
        """Return absolute module and class path"""
        return class_to_path(self.__class__)

    @property
    def get_meta(self) -> ProviderMetadata:
        """Return instance of ProviderMetadata class"""
        return self._meta

    # pylint: disable=unused-argument
    def get_translator(self, data_type: Type) -> ProviderObjectTranslator:
        """Get translator for type. If none available return None"""
        return None

    # pylint: disable=unused-argument
    def get_provider(self, data_type: Type) -> 'BaseProvider':
        """Get provider for type. This function is called if this class has no
        translator for data_type. The returned class will be instantied with the same credentials,
        and will also be checked for translators. Return None if providers are known."""
        return None

    def check_credentials(self, credentials=None) -> bool:
        """Check if Credentials is the correct class and try authentication.
        credentials might be none, in which case credentials from the constructor should be used.
        Should return False if check fails, otherwise True"""
        raise NotImplementedError()

    def check_status(self) -> Union[bool, str]:
        """This is used to check if the provider is reachable
        Expected Return values:
         - True: Everything is ok
         - False: Error (show generic warning)
         - String: Error (show string)"""
        raise NotImplementedError()

    class Meta(ProviderMetadata):
        """Base Provider Meta"""

        def __init__(self, provider):
            super().__init__(provider)
            self.selectable = False
            self.ui_name = _('BaseProvider')


def get_providers(capabilities=None, path=False) -> list:
    """Get all providers, and filter their sub providers"""

    def walk(root):
        """Recursively walk subclasses of <root>"""
        subclasses = root.__subclasses__()
        result = []
        if subclasses != []:
            for subclass in subclasses:
                result += walk(subclass)
        # else:
        if root != BaseProvider:
            result += [root]
        return result

    providers = walk(BaseProvider)
    # Filter out the sub
    valid = []
    for provider in list(set(providers)):
        provider_meta = provider.Meta(None)
        if provider_meta.selectable:
            # Optionally check for matching capabilities
            if capabilities:
                qualified = True
                for capability in capabilities:
                    if capability not in provider_meta.capabilities:
                        qualified = False
                if qualified:
                    valid.append(provider)
            else:
                valid.append(provider)
    # if path is True, convert classes to dotted path
    if path:
        return [class_to_path(provider) for provider in valid]
    return sorted(valid, key=lambda provider: provider.Meta(None).ui_name)
