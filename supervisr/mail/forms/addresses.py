"""supervisr mail Address forms"""

from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from supervisr.mail.models import Address


class AddressForm(ModelForm):
    """Address Form"""

    title = _('General Information')

    class Meta:

        model = Address
        fields = ['mail_address', 'enabled', 'domains', 'providers']
