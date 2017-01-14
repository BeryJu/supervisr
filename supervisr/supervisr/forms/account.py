"""
Supervisr Core Account Forms
"""

import logging
import re

from captcha.fields import ReCaptchaField
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.utils.translation import ugettext as _

from ..ldap_connector import LDAPConnector
from ..models import Setting

LOGGER = logging.getLogger(__name__)

def password_check(form):
    """
    Check if Password adheres to filter and if passwords matche
    """
    password_a = form.cleaned_data.get('password')
    password_b = form.cleaned_data.get('password_rep')
    # Error if one password is empty.
    if not password_b:
        raise forms.ValidationError(_("You must confirm your password"))
    if password_a != password_b:
        raise forms.ValidationError(_("Your passwords do not match"))
    # Check if password is strong enough
    if Setting.get('supervisr:password:filter') is not '':
        if not re.match(Setting.get('supervisr:password:filter'), password_b):
            desc = Setting.get('supervisr:password:filter:description')
            raise forms.ValidationError(_("Password has to contain %(desc)s" % {
                'desc': desc
                }))
    return password_a

class LoginForm(forms.Form):
    """
    Form to handle logins
    """
    email = forms.EmailField(label=_('Mail'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    remember = forms.BooleanField(required=False, label=_('Remember'))
    captcha = ReCaptchaField(
        required=(not settings.DEBUG),
        private_key=Setting.get('supervisr:recaptcha:private'),
        public_key=Setting.get('supervisr:recaptcha:public'))

class SignupForm(forms.Form):
    """
    Form to handle signups
    """
    name = forms.CharField(label=_('Name'))
    email = forms.EmailField(label=_('Mail'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    password_rep = forms.CharField(widget=forms.PasswordInput, label=_('Repeat Password'))
    captcha = ReCaptchaField(
        required=(not settings.DEBUG),
        private_key=Setting.get('supervisr:recaptcha:private'),
        public_key=Setting.get('supervisr:recaptcha:public'))
    tos_accept = forms.BooleanField(required=True, label=_('I accept the Terms of service'))
    news_accept = forms.BooleanField(required=False, label=_('Subscribe to Newsletters'))

    def clean_email(self):
        """
        Check if email is already used in django or in LDAP
        """
        email = self.cleaned_data.get('email')
        # Check if user exists already, error early
        if len(User.objects.filter(email=email)) > 0:
            LOGGER.debug("email %s exists in django", email)
            raise ValidationError(_("Email already exists"))
        # Test if user exists in LDAP
        if LDAPConnector.enabled():
            ldap = LDAPConnector()
            if ldap.is_email_used(email):
                LOGGER.debug("email %s exists in ldap", email)
                raise ValidationError(_("Email already exists"))
        return email

    def clean_password_rep(self):
        """
        Check if Password adheres to filter and if passwords matche
        """
        return password_check(self)

class ChangePasswordForm(forms.Form):
    """
    Form to handle password changes
    """
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    password_rep = forms.CharField(widget=forms.PasswordInput, label=_('Repeat Password'))

    def clean_password_rep(self):
        """
        Check if Password adheres to filter and if passwords matche
        """
        return password_check(self)

class PasswordResetInitForm(forms.Form):
    """
    Form to initiate password resets
    """
    email = forms.EmailField(label=_('Mail'))
    captcha = ReCaptchaField(
        required=(not settings.DEBUG),
        private_key=Setting.get('supervisr:recaptcha:private'),
        public_key=Setting.get('supervisr:recaptcha:public'))

class PasswordResetFinishForm(forms.Form):
    """
    Form to finish password resets
    """
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    password_rep = forms.CharField(widget=forms.PasswordInput, label=_('Repeat Password'))

    def clean_password_rep(self):
        """
        Check if Password adheres to filter and if passwords matche
        """
        return password_check(self)
