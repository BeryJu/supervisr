"""
Supervisr Mail MailAccount Forms
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from supervisr.core.forms.core import check_password
from supervisr.mail.fields import MultiEmailField
from supervisr.mail.models import MailAccount


class MailAccountGeneralForm(forms.Form):
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

    def clean_address(self):
        """
        Check if address is already taken
        """
        domain = self.cleaned_data.get('domain')
        address = self.cleaned_data.get('address')
        accounts = MailAccount.objects.filter(domain=domain, address=address)
        if accounts.exists():
            raise forms.ValidationError("Address '%s' exists already" % accounts.first().email)

        return address

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
        return check_password(self, check_filter=False)

class MailAccountFormAlias(forms.Form):
    """
    Step 3 for Mail Account Creation
    """

    title = 'Optional Forwarder'
    help_text = 'This can be used to forward every email to this address. Optional.'
    alias_dest = MultiEmailField(required=False, label=_('Forwarder destination (optional)'))

    def __init__(self, *args, **kwargs):
        super(MailAccountFormAlias, self).__init__(*args, **kwargs)
        self.fields['alias_dest'].widget.attrs['placeholder'] = _("One destination per line")

    def clean_alias_dest(self):
        """
        Check that no duplicated destination addresses were given
        """
        fwd_list = self.cleaned_data.get('alias_dest')
        if len(fwd_list) != len(set(fwd_list)):
            raise forms.ValidationError('List contains duplicates.')
        return fwd_list

class MailAccountForm(forms.ModelForm):
    """
    Form used to edit accounts
    """

    class Meta:

        fields = ['domain', 'address', 'can_send', 'can_receive', 'is_catchall']
        model = MailAccount
