"""Supervisr Mail MailAlias Forms"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from supervisr.mail.fields import MultiEmailField
from supervisr.mail.models import MailAlias, MailDomain


class MailAliasWizardForm(forms.Form):
    """Create a Mail Alias"""

    request = None
    title = 'General Information'
    help_text = _(('Redirect E-Mails from source to destination. Depending on provider, this will '
                   'either rewrite the recipient address or just redirect the E-Mail.'))
    source = forms.EmailField(label=_('Source address'))
    destination = MultiEmailField(label=_('Destination(s)'))

    def __init__(self, *args, **kwargs):
        super(MailAliasWizardForm, self).__init__(*args, **kwargs)
        self.fields['destination'].widget.attrs['placeholder'] = _("One destination per line")

    def check_source(self):
        """Check that current user has access to source domain"""
        source_address = self.cleaned_data.get('source')
        _local_path, domain = source_address.split('@')
        matching_domains = MailDomain.objects.filter(domain__domain=domain)
        if not matching_domains.exist():
            # Domain does not exist at all
            raise forms.ValidationError("Domain does not exist.")
        if not matching_domains.first().userproductrelationship_set \
          .filter(user=self.request.user).exist():
            # Current user does not have access to domain
            raise forms.ValidationError("No access to domain.")
        return source_address

    def clean_destination(self):
        """Check that no duplicated destination addresses were given"""
        alias_list = self.cleaned_data.get('destination')
        if len(alias_list) != len(set(alias_list)):
            raise forms.ValidationError(_("List contains duplicates."))
        return alias_list

class MailAliasForm(forms.ModelForm):
    """Form used to edit Mail Aliases"""

    class Meta:

        exclude = []
        model = MailAlias
