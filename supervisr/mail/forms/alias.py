"""
Supervisr Mail MailAlias Forms
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from supervisr.mail.fields import MultiEmailField
from supervisr.mail.models import MailAlias


class MailAliasWizardForm(forms.Form):
    """
    Create a Mail Alias
    """

    title = 'General Information'
    help_text = 'This can be used to forward every email to this address.'
    accounts = forms.ModelChoiceField(queryset=None, required=True,
                                      label=_('Source Account'))
    alias_dest = MultiEmailField(required=False, label=_('Alias destination'))

    def __init__(self, *args, **kwargs):
        super(MailAliasWizardForm, self).__init__(*args, **kwargs)
        self.fields['alias_dest'].widget.attrs['placeholder'] = _("One destination per line")

    def clean_alias_dest(self):
        """
        Check that no duplicated destination addresses were given
        """
        alias_list = self.cleaned_data.get('alias_dest')
        if len(alias_list) != len(set(alias_list)):
            raise forms.ValidationError('List contains duplicates.')
        return alias_list

class MailAliasForm(forms.ModelForm):
    """
    Form used to edit Mail Aliases
    """

    class Meta:

        exclude = []
        model = MailAlias
