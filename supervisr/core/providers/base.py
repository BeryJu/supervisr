"""
Supervisr Core Generic Provider
"""

# pylint: disable=too-few-public-methods
class BaseProvider(object):
    """
    Generic Interface as base for GenericManagedProvider and GenericUserProvider
    """

    ui_name = "ui_name hasn't been overriden"
    selectable = True
    credentials = None

    def __init__(self, credentials):
        self.credentials = credentials.cast()

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

    @staticmethod
    def get_providers(filter_sub=None, path=False):
        """
        Get all providers, and filter their sub providers
        """
        def walk(root):
            """
            Recursively walk subclasses of <root>
            """
            # pylint: disable=no-member
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
            if provider.selectable:
                if filter_sub:
                    quallified = True
                    for sub_name in filter_sub:
                        if not getattr(provider, sub_name, False):
                            quallified = False
                    if quallified:
                        valid.append(provider)
                else:
                    valid.append(provider)
        # if path is True, convert classes to dotted path
        if path:
            return ['%s.%s' % (p.__module__, p.__name__) for p in valid]
        return sorted(valid, key=lambda x: x.ui_name)
