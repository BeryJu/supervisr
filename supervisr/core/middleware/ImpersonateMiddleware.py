"""Supervisr Core Middleware to impersonate users"""

from django.contrib.auth.models import User


def impersonate(get_response):
    """Middleware to impersonate users"""

    def middleware(req):
        """Middleware to impersonate users"""

        if req.user.is_superuser and "__impersonate" in req.GET:
            req.session['impersonate_id'] = int(req.GET["__impersonate"])
        elif "__unimpersonate" in req.GET and 'impersonate_id' in req.session:
            del req.session['impersonate_id']
        if req.user.is_superuser and 'impersonate_id' in req.session:
            req.user = User.objects.get(id=req.session['impersonate_id'])

        response = get_response(req)
        return response
    return middleware
