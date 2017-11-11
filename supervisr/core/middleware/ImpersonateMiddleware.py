"""
Supervisr Core Middleware to impersonate users
"""

from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from supervisr.core.utils import messages_add_once


def impersonate(get_response):
    """Middleware to impersonate users"""

    stop_text = _('Stop Impersonating')
    stop_link = mark_safe('<a class="btn alert-action" href="?__unimpersonate=True">%s</a>' \
        % stop_text)

    def middleware(req):
        """Middleware to impersonate users"""

        if req.user.is_superuser and "__impersonate" in req.GET:
            req.session['impersonate_id'] = int(req.GET["__impersonate"])
        elif "__unimpersonate" in req.GET and 'impersonate_id' in req.session:
            del req.session['impersonate_id']
        if req.user.is_superuser and 'impersonate_id' in req.session:
            req.user = User.objects.get(id=req.session['impersonate_id'])
            messages_add_once(req, messages.ERROR, _("You are impersonating %s. %s"
                                                     % (req.user.email, stop_link)))
        response = get_response(req)
        return response
    return middleware
