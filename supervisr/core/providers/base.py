"""
Supervisr Core Generic Provider
"""
from enum import Enum

from django.contrib.auth.models import User
from django.db import models
from django.http import HttpRequest


class ProviderInterfaceAction(Enum):
    """
    Different Actions for Providers
    """
    create = 0
    edit = 2
    delete = 4

# pylint: disable=too-few-public-methods
class BaseProviderInterface(object):
    """
    Base Class for all possible interfaces with a provider, i.e. API or Forms
    """

    provider = None
    action = ProviderInterfaceAction

    def __init__(self, provider, action: ProviderInterfaceAction):
        self.provider = provider
        self.action = action

class BaseProviderUIInterface(BaseProviderInterface):
    """
    Base Class for UI Interaction with provider
    """

    forms = []
    request = HttpRequest

    def __init__(self, provider, action: ProviderInterfaceAction, request: HttpRequest):
        super(BaseProviderUIInterface, self).__init__(provider, action)
        self.request = request

    # pylint: disable=no-self-use,unused-argument
    def get_form_initial(self, index):
        """
        Return Initial form data for form#index
        """
        return {}

    def post_submit(self, form_data):
        """
        This method is called after all forms are filled in and validated.
        The Provider should create it's resources in this step.
        """
        pass

# pylint: disable=too-few-public-methods
class BaseProvider(object):
    """
    Generic Interface as base for GenericManagedProvider and GenericUserProvider
    """

    ui_name = "ui_name hasn't been overriden"

    interface_ui = BaseProviderUIInterface
    setup_ui = BaseProviderUIInterface

    instance = None

    def __init__(self, instance):
        self.instance = instance
        if self.interface_ui:
            self.interface_ui = self.interface_ui()

    @staticmethod
    # pylint: disable=bad-staticmethod-argument
    def walk_providers(cls):
        """
        Walk across all subclasses and return all subclasses which have no children
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
            result += [root]
            return result

        providers = walk(cls)
        # Filter duplicates
        return list(set(providers))

class BaseProviderInstance(models.Model):
    """
    Save information about information specifially for a user
    """

    ui_name = "ui_name hasn't been overriden"

    user = models.ForeignKey(User)

    @property
    def instance_info(self):
        """
        Return information about Instance
        """
        return "instance_info hasn't been overriden"
