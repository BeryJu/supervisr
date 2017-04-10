"""
Supervisr Core utils
"""

import socket
from uuid import uuid4

from django.conf import settings
from django.shortcuts import render
from django.utils.translation import ugettext as _


def get_remote_ip(req):
    """
    Return the remote's IP
    """
    if not req:
        return '0.0.0.0'
    if req.META.get('HTTP_X_FORWARDED_FOR'):
        return req.META.get('HTTP_X_FORWARDED_FOR')
    else:
        return req.META.get('REMOTE_ADDR')

def uuid():
    """
    Return a UUID as string with just alphanumeric-chars
    """
    return str(uuid4()).replace('-', '').upper()

def get_reverse_dns(dev_ip):
    """
    Does a reverse DNS lookup and returns the first IP
    """
    try:
        rev = socket.gethostbyaddr(dev_ip)
        if len(rev) > 0:
            return rev[0]
    except (socket.herror, TypeError, IndexError):
        return ''

def do_404(req, message=None):
    """
    Boilerplate to return a 404 message
    """
    return render(req, 'common/error.html', {
        'code': 404,
        'message': _(message) if message is not None else None
    }, status=404)

def send_admin_mail(exception, message):
    """
    Send Email to all superusers
    """
    from django.contrib.auth.models import User
    from .mailer import send_message
    emails = [x.email for x in User.objects.filter(superuser=True)]
    return send_message(
        recipients=emails,
        subject=_("Supervisr Error %(exception)s" % {
            'exception': exception}),
        template='email/admin_mail.html',
        template_context={'exception': exception, 'message': message})

def get_apps(mod_only=False):
    """
    Get a list of all installed apps
    """
    app_list = []
    for app in settings.INSTALLED_APPS:
        if app.startswith('supervisr') and \
            app is not 'supervisr' and \
            not app.startswith('supervisr.'):
            if mod_only is True:
                if app.startswith('supervisr_mod'):
                    app_list.append(app)
            else:
                app_list.append(app)
    return app_list
