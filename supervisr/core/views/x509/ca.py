"""supervisr core CA views"""

from supervisr.core.models import CA
from supervisr.core.views.generic import (GenericDeleteView, GenericIndexView,
                                          GenericUpdateView)


class CAIndexView(GenericIndexView):
    """List all CAs"""

    model = CA
    template_name = 'x509/ca_index.html'


class CAUpdateView(GenericUpdateView):
    """Update certificate"""

    model = CA
    form = None

    def redirect(self, instance: CA):
        return 'ca-index'


class CADeleteView(GenericDeleteView):
    """Delete certificates"""

    model = CA

    def redirect(self, instance: CA):
        return 'ca-index'
