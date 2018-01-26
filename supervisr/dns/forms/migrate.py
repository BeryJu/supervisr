"""supervisr dns migration forms"""
from django import forms
from django.utils.translation import ugettext_lazy as _


class ZoneImportForm(forms.Form):
    """Zone import form"""
    title = _('Zone Data')

    zone_data = forms.CharField(widget=forms.Textarea, label=_('Zone Data'))

class ZoneImportPreviewForm(forms.Form):
    """Zone import preview form"""
    title = _('Preview Results')

    accept = forms.BooleanField(required=False, initial=True, label=_('Accept Import'))
