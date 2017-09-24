"""
Supervisr Core Base API
"""

from django.http import Http404, QueryDict
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from supervisr.core.api.utils import api_response


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
            return api_response(request, {'error': 'verb not allowed in HTTP VERB'})

        API.init_user_filter(request.user)

        if request.method in ['PUT', 'DELETE']:
            data = QueryDict(request.body).dict()
        elif request.method == 'POST':
            data = request.POST.dict()
        elif request.method == 'GET':
            data = request.GET.dict()

        handler = getattr(self, verb, None)

        self.pre_handler(request, handler)

        if handler:
            try:
                return api_response(request, handler(request, data))
            except Http404:
                return api_response(request, {'error': '404'})
            except KeyError as exc:
                return api_response(request, {'error': exc.args[0]})

    # pylint: disable=unused-argument
    def pre_handler(self, handler, request):
        """
        Optional Handler, which is run before the chosen handler is run
        """
        pass

    @staticmethod
    def init_user_filter(user):
        """
        This method is used to check if the user has access
        """
        if not user.is_authenticated:
            raise Http404
        return True
