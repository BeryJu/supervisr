"""supervisr core emailbackend"""
from logging import getLogger

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError

from supervisr.core.models import SVAnonymousUser

LOGGER = getLogger(__name__)


class EmailBackend(ModelBackend):
    """Authenticate user by E-Mail"""

    def authenticate(self, request, email=None, password=None, **kwargs):
        """Same as default authenticate, except user is searched by E-Mail"""
        user_model = get_user_model()
        try:
            LOGGER.debug("attempting to authenticate %s", email)
            user = user_model.objects.get(email=email)
        except user_model.DoesNotExist:
            LOGGER.debug("User does not exist")
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        LOGGER.debug("User password dont match or cant auth")
        return None


class APIKeyBackend(ModelBackend):
    """Authenticate user by API Key"""

    # pylint: disable=unused-argument
    def authenticate(self, request, **creds):
        """Authenticate based on API Key in request"""
        if not request:
            return None
        user_model = get_user_model()
        try:
            key = SVAnonymousUser.api_key
            if settings.API_KEY_PARAM in request.GET:
                key = request.GET.get(settings.API_KEY_PARAM)
            elif settings.API_KEY_PARAM in request.POST:
                key = request.POST.get(settings.API_KEY_PARAM)
            elif settings.API_KEY_PARAM in request.META:
                key = request.META.get(settings.API_KEY_PARAM)
            LOGGER.debug("Got API key in requerst, attempting to authenticate")
            user = user_model.objects.get(api_key=key)
        except user_model.DoesNotExist:
            return None
        except ValidationError:
            return None
        else:
            if self.user_can_authenticate(user):
                return user
        return None
