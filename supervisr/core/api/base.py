"""
Supervisr Core Base API
"""
import json
import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404, QueryDict
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from supervisr.core.api.utils import api_response

LOGGER = logging.getLogger(__name__)

class API(View):
    """
    Basic API
    """

    ALLOWED_VERBS = {
        'GET': [],
        'POST': [],
    }

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        my_allowed = self.ALLOWED_VERBS[request.method]
        verb = kwargs['verb']
        if verb not in my_allowed:
            return api_response(request, {'error': 'verb not allowed in HTTP VERB', 'code': 400})

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
        except PermissionDenied:
            return api_response(request, {'error': 'permission denied', 'code': 403})
        except KeyError as exc:
            return api_response(request, {'error': exc.args[0], 'code': 404})
        except Http404:
            return api_response(request, {'error': 'not found', 'code': 404})

    # pylint: disable=unused-argument
    def pre_handler(self, handler, request):
        """Optional Handler, which is run before the chosen handler is run"""
        pass

    @staticmethod
    def init_user_filter(user):
        """This method is used to check if the user has access"""
        if not user.is_authenticated:
            raise PermissionDenied
        return True
