"""
Supervisr Mail MailAccount Forms
"""

from django import forms
from django.utils.translation import ugettext as _


class NewMailAccountStep1Form(forms.Form):
    """
    Initial MailAccount Creation Form
    """

    KIND_NORMAL_ACCOUNT = 0
    KIND_FORWARDER = 1
    KIND_SEND_ONLY = 2
    KIND_RECEIVE_ONLY = 3
    KIND = (
        (KIND_NORMAL_ACCOUNT, _('Normal Account')),
        (KIND_FORWARDER, _('Forwarder')),
        (KIND_SEND_ONLY, _('Send Only')),
        (KIND_RECEIVE_ONLY, _('Receive Only')),
    )
    address = forms.EmailField(label=_('Address'))
    kind = forms.ChoiceField(choices=KIND, label=_('Kind'))

# class NewMailAccount
