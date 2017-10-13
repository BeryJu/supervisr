from django import forms
from django.utils.translation import ugettext as _


class ZoneImportForm(forms.Form):

    title = _('Zone Data')

    zone_data = forms.CharField(widget=forms.Textarea, label=_('Zone Data'))

class ZoneImportPreviewForm(forms.Form):

    title = _('Preview Results')

    accept = forms.BooleanField(required=False, initial=True, label=_('Accept Import'))
