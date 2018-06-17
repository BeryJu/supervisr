"""supervisr mail maildomain forms"""

from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from supervisr.mail.models import MailDomain


class MailDomainForm(ModelForm):
    """MailDomain Form"""

    title = _('General Information')

    class Meta:

        model = MailDomain
        fields = ['domain', 'providers', 'enabled']
