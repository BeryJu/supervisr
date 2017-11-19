"""
Supervisr Core Account APIv1
"""

from supervisr.core.api.models import ModelAPI
from supervisr.core.models import User


class AccountAPI(ModelAPI):
    """Account API"""

    model = User

    editable_fields = []

    ALLOWED_VERBS = {
        'GET': ['me']
    }

    # pylint: disable=invalid-name,unused-argument
    def me(self, request, data):
        """Return ourselves as dict"""
        user_data = {}
        for field in ['pk', 'first_name', 'email', 'username']:
            user_data[field] = getattr(request.user, field)
        user_data['id'] = request.user.pk
        return user_data
