"""Supervisr Core Credential APIv1"""

from supervisr.core.api.models import UserAcquirableModelAPI
from supervisr.core.forms.users import EditUserForm
from supervisr.core.models import User


class UserAPI(UserAcquirableModelAPI):
    """User API"""

    model = User
    form = EditUserForm
