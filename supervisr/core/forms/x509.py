"""supervisr core x509 forms"""

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from django import forms
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext_lazy as _


class CertificateImportForm(forms.Form):
    """Form to import a certificate from PEM"""

    title = _('PEM Data')
    pem = forms.CharField(widget=forms.Textarea, label=_('PEM'))

    def clean_pem(self):
        """Verify that `self.pem` is actually a valid certificate"""
        try:
            x509.load_pem_x509_certificate(force_bytes(self.cleaned_data.get('pem')),
                                           default_backend())
        except ValueError as exc:
            raise forms.ValidationError from exc
        return self.cleaned_data.get('pem')
