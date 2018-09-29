"""supervisr dns migration forms"""
from django import forms
from django.utils.translation import ugettext_lazy as _
from dns.zone import BadZone

from supervisr.dns.utils import import_bind


class ZoneImportForm(forms.Form):
    """Zone import form"""

    title = _('Zone Data')
    zone_data = forms.CharField(widget=forms.Textarea, label=_('Zone Data'))

    def clean_zone_data(self):
        """Check if zone is valid"""
        zone_data = self.cleaned_data.get('zone_data')
        try:
            import_bind(zone_data)
        except BadZone:
            raise forms.ValidationError(_('Invalid Zone Data'))
        return zone_data


class ZoneImportPreviewForm(forms.Form):
    """Zone import preview form"""

    title = _('Preview Results')
    accept = forms.BooleanField(required=False, initial=True, label=_('Accept Import'))
    records = []
