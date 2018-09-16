"""supervisr core certificate views"""
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.utils.translation import ugettext_lazy as _

from supervisr.core.forms.x509 import CertificateImportForm
from supervisr.core.models import Certificate, UserAcquirableRelationship
from supervisr.core.views.generic import (GenericDeleteView, GenericIndexView,
                                          GenericUpdateView)
from supervisr.core.views.wizards import BaseWizardView


class CertificateIndexView(GenericIndexView):
    """List all certificates"""

    model = Certificate
    template_name = 'x509/certificate_index.html'

class CertificateUpdateView(GenericUpdateView):
    """Update certificate"""

    model = Certificate
    form = None

    def redirect(self, instance: Certificate):
        return 'certificate-index'

class CertificateDeleteView(GenericDeleteView):
    """Delete certificates"""

    model = Certificate

    def redirect(self, instance: Certificate):
        return 'certificate-index'

class ImportWizard(BaseWizardView):
    """Wizard to import certificate from PEM Data"""

    title = _('Certificate Import')
    form_list = [CertificateImportForm]

    def finish(self, form_list) -> HttpResponse:
        cert = Certificate.from_pem(form_list[0].cleaned_data.get('pem'))
        cert.save()
        UserAcquirableRelationship.objects.create(
            model=cert,
            user=self.request.user)
        return redirect(reverse('certificate-index'))
