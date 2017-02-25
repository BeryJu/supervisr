"""
Supervisr Mail MailAccount Forms
"""

from django import forms
from form_utils.forms import BetterForm
from django.utils.translation import ugettext as _
from ..models import MailDomain

class MailAccountForm(BetterForm):
    """
    Initial MailAccount Creation Form
    """

    KIND_NORMAL = 0
    KIND_FORWARDER = 1
    KIND_SEND_ONLY = 2
    KIND_RECEIVE_ONLY = 3
    KIND = (
        (KIND_NORMAL, _('Normal Account')),
        (KIND_FORWARDER, _('Forwarder')),
        (KIND_SEND_ONLY, _('Send Only')),
        (KIND_RECEIVE_ONLY, _('Receive Only')),
    )
    domain = forms.ModelChoiceField(queryset=None, required=True,
                                    to_field_name='name', label=_('Domain'))
    address = forms.CharField(max_length=64, label=_('Address'))
    kind = forms.ChoiceField(widget=forms.RadioSelect, choices=KIND, label=_('Kind'))

    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    password_rep = forms.CharField(widget=forms.PasswordInput, label=_('Repeat Password'))

    forwarder_dest = forms.EmailField(label=_('Forwarder Destination'))

    class Meta:
        fieldsets = [('step-1', {'fields': ['domain', 'address', 'kind'],
                                   'legend': _('Step 1'),
                                   'description': _('General Informaion')}),
                     ('step-2', {'fields': ['password', 'password_rep'],
                                   'legend': _('Step 2'),
                                   'description': _('Credentials for this Mail Account'),
                                   'classes': ['optional-kind-not=1']}),
                     ('step-2', {'fields': ['forwarder_dest'],
                                   'legend': _('Step 2'),
                                   'description': _('Forwarder Destination'),
                                   'classes': ['optional-kind-only=1']})]


