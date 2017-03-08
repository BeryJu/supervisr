"""
Supervisr 2FA Forms
"""

from django import forms
from django.utils.translation import ugettext as _

from supervisr.forms.core import InlineForm


class TFAVerifyForm(InlineForm):
    """
    Step 3 for Mail Account Creation
    """
    order = ['code']
    code = forms.IntegerField(label=_('Code'))
