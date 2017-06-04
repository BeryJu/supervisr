"""
Supervisr Core User Forms
"""


from django import forms

from .core import InlineForm


class EditUserForm(InlineForm):
    """
    Form to edit a User
    """

    order = ['name', 'email', 'username', 'unix_username', 'unix_userid']
    name = forms.CharField(label='Name')
    email = forms.CharField(label='Email', disabled=True, required=False)
    username = forms.CharField(label='Username', disabled=True, required=False)
    unix_username = forms.CharField(label='Unix Username', disabled=True, required=False)
    unix_userid = forms.CharField(label='Unix ID', disabled=True, required=False)
