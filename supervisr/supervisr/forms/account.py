from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from ..ldap_connector import LDAPConnector
from captcha.fields import ReCaptchaField

class AuthenticationForm(forms.Form):
    email = forms.EmailField(label=_('Mail'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    remember = forms.BooleanField(required=False, label=_('Remember'))
#    captcha = ReCaptchaField()

    def clean_mail(self):
        email = self.cleaned_data.get('email')
        # Check if user exists already, error early
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Email already exists"))
        # Test if user exists in LDAP
        if LDAPConnector.enabled():
            ldap = LDAPConnector()
            if ldap.is_email_used(email):
                raise ValidationError(_("Email already exists"))
        return mail

class SignupForm(forms.Form):
    email = forms.EmailField(label=_('Mail'))
    name = forms.CharField(label=_('Name'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    password_rep = forms.CharField(widget=forms.PasswordInput, label=_('Repeat Password'))
#    captcha = ReCaptchaField()
    tos_accept = forms.BooleanField(required=True, label=_('I accept the Terms of service'))
    news_accept = forms.BooleanField(required=False, label=_('Subscribe to Newsletters'))

    def clean_mail(self):
        email = self.cleaned_data.get('email')
        # Check if user exists already, error early
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Email already exists"))
        # Test if user exists in LDAP
        if LDAPConnector.enabled():
            ldap = LDAPConnector()
            if ldap.is_email_used(email):
                raise ValidationError(_("Email already exists"))
        return mail

    def clean_password_rep(self):
        password_a = self.cleaned_data.get('password')
        password_b = self.cleaned_data.get('password_rep')
        # Error if one password is empty.
        if not password_b:
            raise forms.ValidationError(_("You must confirm your password"))
        if password_a != password_b:
            raise forms.ValidationError(_("Your passwords do not match"))
        return password_b
