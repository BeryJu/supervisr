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

from ..models import Setting
from ..signals import SIG_CHECK_USER_EXISTS
from .core import InlineForm

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

class LoginForm(InlineForm):
    """
    Form to handle logins
    """
    order = ['email', 'password', 'remember', 'captcha']
    email = forms.EmailField(label=_('Mail'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    remember = forms.BooleanField(required=False, label=_('Remember'))
    captcha = ReCaptchaField(
        required=(not settings.DEBUG),
        private_key=Setting.get('supervisr:recaptcha:private'),
        public_key=Setting.get('supervisr:recaptcha:public'))

class SignupForm(InlineForm):
    """
    Form to handle signups
    """
    order = ['name', 'email', 'password', 'password_rep', 'captcha', 'tos_accept', 'news_accept']
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
        results = SIG_CHECK_USER_EXISTS.send(
            sender=SignupForm,
            email=email)
        for handler, result in results:
            if result is not False:
                LOGGER.debug("email %s exists in %s", email, handler.__name__)
                raise ValidationError(_("Email already exists"))
        return email

    def clean_password_rep(self):
        """
        Check if Password adheres to filter and if passwords matche
        """
        return password_check(self)

class ChangePasswordForm(InlineForm):
    """
    Form to handle password changes
    """
    order = ['password', 'password_rep']
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    password_rep = forms.CharField(widget=forms.PasswordInput, label=_('Repeat Password'))

    def clean_password_rep(self):
        """
        Check if Password adheres to filter and if passwords matche
        """
        return password_check(self)

class PasswordResetInitForm(InlineForm):
    """
    Form to initiate password resets
    """
    order = ['email', 'captcha']
    email = forms.EmailField(label=_('Mail'))
    captcha = ReCaptchaField(
        required=(not settings.DEBUG),
        private_key=Setting.get('supervisr:recaptcha:private'),
        public_key=Setting.get('supervisr:recaptcha:public'))

class PasswordResetFinishForm(InlineForm):
    """
    Form to finish password resets
    """
    order = ['password', 'password_rep']
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    password_rep = forms.CharField(widget=forms.PasswordInput, label=_('Repeat Password'))

    def clean_password_rep(self):
        """
        Check if Password adheres to filter and if passwords matche
        """
        return password_check(self)
