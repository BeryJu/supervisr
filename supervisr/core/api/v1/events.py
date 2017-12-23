"""
Supervisr Core Event APIv1
"""

from supervisr.core.api.models import ModelAPI
from supervisr.core.models import Event


class EventAPI(ModelAPI):
    """Event API"""

    model = Event
    viewable_fields = ['user', 'message', 'create_timestamp']

    def user_filter(self, queryset, user):
        """This method is used to check if the user has access"""
        super(EventAPI, self).user_filter(queryset, user)
        return queryset.filter(user=user)
