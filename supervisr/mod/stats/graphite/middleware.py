"""
Supervisr Core Middleware to detect Maintenance Mode
"""

import time

from django.contrib import messages
from django.core.urlresolvers import resolve
from django.utils.translation import ugettext as _

from supervisr.core.models import Setting
from supervisr.mod.stats.graphite.graphite_client import (GraphiteClient,
                                                          GraphiteException)


def stats(get_response):
    """
    Middleware get stats
    """

    def middleware(req):
        """
        Middleware get stats
        """
        before = time.time()
        response = get_response(req)
        after = time.time()

        if Setting.objects.get(pk='enabled').value_bool:
            try:
                with GraphiteClient() as client:
                    res_match = resolve(req.path_info).func
                    view_path = (res_match.__module__ + '.' + res_match.__name__).replace('.', '::')
                    client.write('views.%s.duration' % view_path, (after - before) * 1000)
                    client.write('views.%s.status.%s' % (view_path, response.status_code), 1)
                    client.write('views.%s.count' % view_path, 1)
            except GraphiteException as exc:
                if req.user.is_authenticated and req.user.is_superuser:
                    # Only show message if logged in and superuser
                    messages.error(req, _("Graphite Error: %(msg)s" % {'msg': str(exc)}))
        return response
    return middleware
