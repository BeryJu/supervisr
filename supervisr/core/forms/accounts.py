"""Supervisr Core Account Forms"""

import logging

from captcha.fields import ReCaptchaField
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from supervisr.core.forms.utils import check_password
from supervisr.core.models import Setting, User
from supervisr.core.signals import on_check_user_exists

LOGGER = logging.getLogger(__name__)


class LoginForm(forms.Form):
    """Form to handle logins"""

    email = forms.EmailField(label=_('Mail'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    remember = forms.BooleanField(required=False, label=_('Remember'))
    captcha = ReCaptchaField(
        required=(not settings.DEBUG and not settings.TEST),
        private_key=Setting.get('recaptcha:private'),
        public_key=Setting.get('recaptcha:public'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not Setting.get_bool('recaptcha:enabled'):
            self.fields.pop('captcha')


class SignupForm(forms.Form):
    """Form to handle signups"""

    name = forms.CharField(label=_('Name'))
    username = forms.CharField(label=_('Username'))
    email = forms.EmailField(label=_('E-Mail'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    password_rep = forms.CharField(widget=forms.PasswordInput, label=_('Repeat Password'))
    captcha = ReCaptchaField(
        required=(not settings.DEBUG and not settings.TEST),
        private_key=Setting.get('recaptcha:private'),
        public_key=Setting.get('recaptcha:public'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not Setting.get_bool('recaptcha:enabled'):
            self.fields.pop('captcha')

    def clean_username(self):
        """Check if username is used already"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            LOGGER.warning("Username %s already exists", username)
            raise ValidationError(_("Username already exists"))
        return username

    def clean_email(self):
        """Check if email is already used in django or other auth sources"""
        email = self.cleaned_data.get('email')
        # Check if user exists already, error early
        if User.objects.filter(email=email).exists():
            LOGGER.debug("email %s exists in django", email)
            raise ValidationError(_("Email already exists"))
        results = on_check_user_exists.send(
            sender=SignupForm,
            email=email)
        for handler, result in results:
            if result is not False:
                LOGGER.debug("email %s exists in %s", email, handler.__name__)
                raise ValidationError(_("Email already exists"))
        return email

    def clean_password_rep(self):
        """Check if Password adheres to filter and if passwords matche"""
        return check_password(self)


class ChangePasswordForm(forms.Form):
    """Form to handle password changes"""

    password_old = forms.CharField(widget=forms.PasswordInput, label=_('Current Password'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    password_rep = forms.CharField(widget=forms.PasswordInput, label=_('Repeat Password'))

    def clean_password_old(self):
        """Check if old password can authenticate user"""
        user = authenticate(email=self.request.user.email,
                            password=self.cleaned_data.get('password_old'),
                            request=self.request)
        if user != self.request.user:
            raise ValidationError(_('Invalid Current Password'))
        return self.cleaned_data.get('password_old')

    def clean_password_rep(self):
        """Check if Password adheres to filter and if passwords matche"""
        return check_password(self)


class PasswordResetInitForm(forms.Form):
    """Form to initiate password resets"""

    email = forms.EmailField(label=_('Mail'))
    captcha = ReCaptchaField(
        required=(not settings.DEBUG),
        private_key=Setting.get('recaptcha:private'),
        public_key=Setting.get('recaptcha:public'))


class PasswordResetFinishForm(forms.Form):
    """Form to finish password resets"""

    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    password_rep = forms.CharField(widget=forms.PasswordInput, label=_('Repeat Password'))

    def clean_password_rep(self):
        """Check if Password adheres to filter and if passwords matche"""
        return check_password(self)


class ReauthForm(forms.Form):
    """Form to reauthenticate users"""

    email = forms.EmailField(disabled=True, label=_('E-Mail'), required=False)
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))


class EmailMissingForm(forms.Form):
    """Form to ask user for email address if theirs is not set"""

    email = forms.EmailField(label=_('E-Mail'), required=True)
