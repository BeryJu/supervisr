"""Supervisr Core Base API"""
import json
import logging

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, QueryDict
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from supervisr.core.api.utils import api_response
from supervisr.core.exceptions import UnauthorizedException

LOGGER = logging.getLogger(__name__)


class API(View):
    """Basic API"""

    ALLOWED_VERBS = {
        'GET': [],
        'POST': [],
    }

    # pylint: disable=too-many-return-statements
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        my_allowed = self.ALLOWED_VERBS[request.method]
        verb = kwargs.get('verb', '')
        if verb not in my_allowed:
            return api_response(request, {'error': 'verb not allowed in HTTP VERB'}, code=400)

        # Check if API Key in request, if so try to authenticate with it
        self.authenticate_with_key(request)

        if request.method in ['PUT', 'DELETE']:
            data = QueryDict(request.body).dict()
        elif request.method == 'POST':
            data = request.POST.dict()
        elif request.method == 'GET':
            data = request.GET.dict()

        if data == {} and request.body.decode('utf-8') != '':
            # data was no form-encoded, so parse JSON from request body
            data = json.loads(request.body.decode('utf-8'))

        handler = getattr(self, verb, None)

        try:
            self.init_user_filter(request.user)
            self.pre_handler(request, handler)
            if handler:
                result = handler(request, data)
                return api_response(request, {'code': 200, 'data': result})
        except UnauthorizedException:
            return api_response(request, {'data': {'error': 'unauthorized'}}, code=401)
        except PermissionDenied:
            return api_response(request, {'data': {'error': 'permission denied'}}, code=403)
        except KeyError as exc:
            return api_response(request, {'data': {'error': exc.args[0]}}, code=404)
        except Http404:
            return api_response(request, {'data': {'error': 'not found'}}, code=404)
        except Exception: # pylint: disable=broad-except
            if settings.DEBUG:
                raise
            return api_response(request, {'data': {'error': 'unknown error'}}, code=500)
        return api_response(request, {'data': {'error': 'unknown error'}}, code=500)

    def pre_handler(self, handler, request):
        """Optional Handler, which is run before the chosen handler is run"""
        pass

    @staticmethod
    def init_user_filter(user):
        """This method is used to check if the user has access"""
        if not user.is_authenticated:
            raise UnauthorizedException
        return True

    def authenticate_with_key(self, request: HttpRequest):
        """Try to authenticate with request data"""
        if settings.API_KEY_PARAM in request.GET or \
                settings.API_KEY_PARAM in request.POST or \
                settings.API_KEY_PARAM in request.META:

            user = authenticate(request)
            if user:
                django_login(request, user)
