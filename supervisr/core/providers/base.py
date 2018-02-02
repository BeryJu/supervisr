"""
Supervisr Core Generic Provider
"""

from django.utils.translation import ugettext_lazy as _


# pylint: disable=too-few-public-methods
class ProviderMetadata(object):
    """
    This is a class to store metadata like ui_name etc about a provider
    """

    selectable = True
    ui_name = "ui_name hasn't been overridden"
    ui_description = "ui_description hasn't been overridden"
    provider = None

    def __init__(self, provider):
        self.provider = provider
        self.ui_name = _(self.ui_name)
        self.ui_description = _(self.ui_description)

    def get_capabilities(self):
        """
        Return all subproviders this provider has
        """
        capabilities = []
        suffix = '_provider'
        for prop in dir(self.provider):
            if prop.endswith(suffix):
                capabilities.append(prop.replace(suffix, ''))
        return capabilities

# pylint: disable=too-few-public-methods
class BaseProvider(object):
    """
    Generic Interface as base for GenericManagedProvider and GenericUserProvider
    """

    credentials = None
    _meta = None

    def __init__(self, credentials=None):
        self._meta = self.Meta(self)
        if credentials:
            self.credentials = credentials.cast()

    @property
    def dotted_path(self):
        """
        Return absolute module and class path
        """
        return '%s.%s' % (self.__module__, self.__class__.__name__)

    @property
    def get_meta(self) -> ProviderMetadata:
        """
        Return instance of ProviderMetadata class
        """
        return self._meta

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

    class Meta(ProviderMetadata):
        """
        Base Provider Meta
        """

        def __init__(self, provider):
            super(BaseProvider.Meta, self).__init__(provider)
            self.selectable = False
            self.ui_name = _('BaseProvider')

def get_providers(filter_sub=None, path=False):
    """
    Get all providers, and filter their sub providers
    """
    def walk(root):
        """
        Recursively walk subclasses of <root>
        """
        sub = root.__subclasses__()
        result = []
        if sub != []:
            for _sub in sub:
                result += walk(_sub)
        # else:
        if root != BaseProvider:
            result += [root]
        return result

    providers = walk(BaseProvider)
    # Filter out the sub
    valid = []
    for provider in list(set(providers)):
        provider_inst = provider()
        if provider_inst._meta.selectable:
            if filter_sub:
                quallified = True
                for sub_name in filter_sub:
                    if not getattr(provider, sub_name, False):
                        quallified = False
                if quallified:
                    valid.append(provider_inst)
            else:
                valid.append(provider_inst)
    # if path is True, convert classes to dotted path
    if path:
        return ['%s.%s' % (p.__module__, p.__class__.__name__) for p in valid]
    return sorted(valid, key=lambda x: x.get_meta.ui_name)
