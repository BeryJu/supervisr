"""
Supervisr Mail MailAccount Forms
"""

from django import forms
from django.utils.translation import ugettext as _

from supervisr.forms.core import check_password


class MailAccountForm(forms.Form):
    """
    Initial MailAccount Creation Form
    """

    title = 'General Information'
    domain = forms.ModelChoiceField(queryset=None, required=True,
                                    label=_('Domain'))
    address = forms.CharField(max_length=64, label=_('Address'))
    can_send = forms.BooleanField(required=False, initial=True,
                                  label=_('Can Send Emails'))
    can_receive = forms.BooleanField(required=False, initial=True,
                                     label=_('Can Receive Emails'))
    is_catchall = forms.BooleanField(required=False, initial=False,
                                     label=_('Mark as Catch-all Account'))

class MailAccountFormCredentials(forms.Form):
    """
    Step 2 for Mail Account Creation
    """

    title = 'Credentials'
    help_text = ("Credentials are optional, but if they are left empty, "
                 "no one can sign into this account.")
    password = forms.CharField(required=False, widget=forms.PasswordInput,
                               label=_('Password'))
    password_rep = forms.CharField(required=False, widget=forms.PasswordInput,
                                   label=_('Repeat Password'))

    def clean_password_rep(self):
        """
        Check if Password adheres to filter and if passwords matche
        """
        return check_password(self)

class MailAccountFormForwarder(forms.Form):
    """
    Step 3 for Mail Account Creation
    """

    title = 'Forwarder Destination'
    help_text = 'This can be used to forward every email to this address. Optional.'
    forwarder_dest = forms.EmailField(required=False, label=_('Forwarder Destination (optional)'))
