
from enum import Enum


class ProviderCommitAction(Enum):

    CREATE = 1
    UPDATE = 2
    DELETE = 4
    DO_NOTHING = 8

class ProviderCommitChange(object):

    object = None
    action = ProviderCommitAction.DO_NOTHING
    content = ''
