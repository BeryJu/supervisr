"""
Supervisr DNS Record Forms
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from supervisr.dns.models import Record


class RecordForm(forms.ModelForm):
    """
    Create/edit RecordForm
    """

    title = _('General Information')

    def clean_name(self):
        """Make sure name doesn't end with `.`"""
        name = self.cleaned_data.get('name')
        if name[-1] == '.':
            raise ValidationError(_('Name may not end with dot.'), code='invalid')
        return name

    class Meta:

        model = Record
        fields = ['domain', 'name', 'resource_set']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': "Set to '@' for root-level records."}),
        }
