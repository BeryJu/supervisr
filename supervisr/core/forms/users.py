"""
Supervisr Core User Forms
"""


from django import forms
from django.utils.translation import ugettext_lazy as _


class EditUserForm(forms.Form):
    """
    Form to edit a User
    """

    order = ['name', 'email', 'username', 'unix_username', 'unix_userid']
    name = forms.CharField(label=_('Name'))
    email = forms.CharField(label=_('Email'), disabled=True, required=False)
    username = forms.CharField(label=_('Username'))
    unix_username = forms.CharField(label=_('Unix Username'), disabled=True, required=False)
    unix_userid = forms.CharField(label=_('Unix ID'), disabled=True, required=False)

class FeedbackForm(forms.Form):
    """
    Form to send feedback
    """

    order = ['email', 'message', 'send_system_info']
    email = forms.CharField(label=_('Email'), disabled=True, required=False)
    message = forms.CharField(widget=forms.Textarea, label=_('Message'))
    send_system_info = forms.BooleanField(label=_('Send System Information?'), required=False)
