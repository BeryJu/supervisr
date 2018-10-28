"""Supervisr Core User Forms"""
from glob import glob
from os import path

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from supervisr.core.models import Setting


class EditUserForm(forms.Form):
    """Form to edit a User"""

    name = forms.CharField(label=_('Name'), required=False)
    email = forms.CharField(label=_('Email'), required=Setting.get_bool('account:email:required'))
    username = forms.CharField(label=_('Username'))
    unix_username = forms.CharField(label=_('Unix Username'), disabled=True, required=False)
    unix_userid = forms.CharField(label=_('Unix ID'), disabled=True, required=False)
    theme = forms.ChoiceField(label=_('Theme'), choices=())
    rows_per_page = forms.IntegerField(label=_('Rows per page'))
    api_key = forms.CharField(label=_('API Key'), disabled=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        css_files = glob(path.join(settings.STATIC_ROOT, "css/*.theme.css"))
        choices = []
        for theme in css_files:
            filename = path.basename(theme)
            themename = filename.replace('.theme.css', '')
            choices.append((themename, themename.title()))
        self.fields['theme'].choices = choices


class FeedbackForm(forms.Form):
    """Form to send feedback"""

    email = forms.CharField(label=_('Email'), disabled=True, required=False)
    message = forms.CharField(widget=forms.Textarea, label=_('Message'))
    send_system_info = forms.BooleanField(label=_('Send System Information?'), required=False)
