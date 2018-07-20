"""supervisr mod web_proxy views"""
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from revproxy.views import ProxyView
from supervisr.core.views.common import ErrorResponseView
from supervisr.mod.web_proxy.models import WebApplication


class Proxy(ProxyView):
    """Proxy View, check access before proxying"""

    def dispatch(self, request: HttpRequest, slug: str, path: str) -> HttpResponse:
        """Check if application exists and load upstream"""
        app = get_object_or_404(WebApplication, access_slug=slug)
        # superusers always get access (for now)
        if not app.has_user(request.user) and not request.user.is_superuser:
            raise Http404
        self.upstream = app.upstream
        # Current user is added as REMOTE_USER
        if app.add_remote_user:
            self.add_remote_user = True
        from urllib3.exceptions import RequestError
        try:
            response = super(Proxy, self).dispatch(request, path)
        except RequestError as exc:
            return ErrorResponseView.as_view()(request, message=str(exc))
        return response
