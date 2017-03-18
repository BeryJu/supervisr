"""
Supervisr 2FA Forms
"""

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from supervisr.forms.core import InlineForm


class PictureWidget(forms.widgets.Widget):
    """
    Widget to render value as img-tag
    """

    def render(self, name, value, attrs=None):
        return mark_safe("<img src=\"%s\" />" % value)

class TFAVerifyForm(InlineForm):
    """
    Simple Form to verify 2FA Code
    """
    order = ['code']
    code = forms.IntegerField(label=_('Code'))

class TFASetupInitForm(forms.Form):
    """
    Initial 2FA Setup form
    """
    title = _('Set up 2FA')
    device = None
    confirmed = False
    qr_code = forms.CharField(widget=PictureWidget, disabled=True, required=False, \
        label=_('Scan this Code with your 2FA App.'))
    code = forms.IntegerField(label=_('Current Code'))

    def clean_code(self):
        """
        Check code with new totp device
        """
        if self.device is not None:
            if not self.device.verify_token(int(self.cleaned_data.get('code'))) \
                and not self.confirmed:
                raise forms.ValidationError(_("2FA Code does not match"))
        return self.cleaned_data.get('code')

class TFASetupStaticForm(forms.Form):
    """
    Static form to show generated static tokens
    """
    tokens = forms.MultipleChoiceField(disabled=True, required=False)
