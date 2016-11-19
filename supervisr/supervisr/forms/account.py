from django import forms
from django.utils.translation import ugettext as _
from captcha.fields import ReCaptchaField

class AuthenticationForm(forms.Form):
    mail = forms.EmailField(label=_('Mail'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    remember = forms.BooleanField(required=False, label=_('Remember'))
    captcha = ReCaptchaField()

class SignupForm(forms.Form):
    mail = forms.EmailField(label=_('Mail'))
    name = forms.CharField(label=_('Name'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    password_rep = forms.CharField(widget=forms.PasswordInput, label=_('Repeat Password'))
    captcha = ReCaptchaField()
    tos_accept = forms.BooleanField(required=True, label=_('I accept the Terms of service'))
    news_accept = forms.BooleanField(required=False, label=_('Subscribe to Newsletters'))
