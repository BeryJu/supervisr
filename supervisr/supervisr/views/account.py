"""
Supervisr Core Account Views
"""

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_GET

from ..controllers import AccountController
from ..decorators import anonymous_required
from ..forms.account import (ChangePasswordForm, LoginForm,
                             PasswordResetFinishForm, PasswordResetInitForm,
                             SignupForm)
from ..ldap_connector import LDAPConnector
from ..mailer import Mailer
from ..models import (ACCOUNT_CONFIRMATION_KIND_PASSWORD_RESET,
                      ACCOUNT_CONFIRMATION_KIND_SIGN_UP, AccountConfirmation)

LOGGER = logging.getLogger(__name__)

@anonymous_required
def login(req):
    """
    View to handle Browser Logins Requests
    """
    if req.method == 'POST':
        form = LoginForm(req.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('password'))
            if user is not None:
                django_login(req, user)
                if form.cleaned_data.get('remember') is True:
                    req.session.set_expiry(settings.REMEMBER_SESSION_AGE)
                else:
                    req.session.set_expiry(0) # Expires when browser is closed
                messages.success(req, _("Successfully logged in!"))
                LOGGER.info("Successfully logged in %s", form.cleaned_data.get('email'))
                return redirect(reverse('common-index'))
            else:
                # Check if the user's account is pending
                # and inform that, they need to check their emails
                users = User.objects.filter(username=form.cleaned_data.get('email'))
                if users.exists():
                    user = users[0]
                    acc_conf = AccountConfirmation.objects.get(user=user)
                    if not acc_conf.confirmed:
                        # Create url to resend email
                        url = reverse('account-confirmation_resend',
                                      kwargs={'email': user.email})
                        messages.error(req, _(('Account not confirmed yet. Check your emails. '
                                               'Click <a href="%(url)s">here</a> to resend the '
                                               'email.')) % {'url': url})
                else:
                    messages.error(req, _("Invalid Login"))
                    LOGGER.info("Failed to log in %s", form.cleaned_data.get('email'))
                return redirect(reverse('account-login'))
    else:
        form = LoginForm()
    return render(req, 'account/login.html', {'form': form})

@anonymous_required
def signup(req):
    """
    View to handle Browser Signups Requests
    """
    if req.method == 'POST':
        form = SignupForm(req.POST)
        if form.is_valid():
            # Create user
            if not AccountController.signup(
                    email=form.cleaned_data.get('email'),
                    name=form.cleaned_data.get('name'),
                    password=form.cleaned_data.get('password')):
                messages.error(req, _("Failed to sign up."))
                return redirect(reverse('account-login'))
            messages.success(req, _("Successfully signed up!"))
            LOGGER.info("Successfully signed up %s",
                        form.cleaned_data.get('email'))
            return redirect(reverse('account-login'))
    else:
        form = SignupForm()
    return render(req, 'account/generic_account_form.html', {
        'form': form,
        'title': _("Signup"),
        'primary_action': _("Signup")
        })

@login_required
def change_password(req):
    """
    View to handle Browser change_password Requests
    """
    if req.method == 'POST':
        form = ChangePasswordForm(req.POST)
        if form.is_valid():
            if not AccountController.change_password(
                    email=req.user.email,
                    password=form.cleaned_data.get('password')):
                messages.error(req, _("Failed to change password"))
            else:
                messages.success(req, _("Successfully changed password!"))
            return redirect(reverse('common-index'))
    else:
        form = ChangePasswordForm()
    return render(req, 'account/generic_account_form.html', {
        'form': form,
        'title': _("Change Password"),
        'primary_action': _("Change Password")
        })

@login_required
@require_GET
def logout(req):
    """
    View to handle Browser logout Requests
    """
    django_logout(req)
    messages.success(req, _("Successfully logged out!"))
    return redirect(reverse('common-index'))

@anonymous_required
@require_GET
def confirm(req, uuid):
    """
    View to handle Browser account_confirm Requests
    """
    if AccountConfirmation.objects.filter(
            pk=uuid,
            kind=ACCOUNT_CONFIRMATION_KIND_SIGN_UP).exists():
        acc_conf = AccountConfirmation.objects.get(pk=uuid)
        if acc_conf.confirmed:
            messages.error(req, _("Account already confirmed!"))
            return redirect(reverse('account-login'))
        if acc_conf.is_expired:
            messages.error(req, _("Confirmation expired"))
            return redirect(reverse('account-login'))
        # activate django user
        acc_conf.user.is_active = True
        acc_conf.user.save()
        # activate LDAP user
        if LDAPConnector.enabled():
            ldap = LDAPConnector()
            ldap.enable_user(acc_conf.user.email)
        # invalidate confirmation
        acc_conf.confirmed = True
        acc_conf.save()
        messages.success(req, _("Account successfully activated!"))
    else:
        raise Http404
    return redirect(reverse('account-login'))

@anonymous_required
def reset_password_init(req):
    """
    View to handle Browser account password reset initiation Requests
    """
    if req.method == 'POST':
        form = PasswordResetInitForm(req.POST)
        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data.get('email'))
            pass_conf = AccountConfirmation.objects.create(
                user=user,
                kind=ACCOUNT_CONFIRMATION_KIND_PASSWORD_RESET)
            if Mailer.send_password_reset_confirm(
                    user.email, pass_conf):
                messages.success(req, _('Reset Link sent successfully'))
            else:
                messages.error(req, _('Failed to send Link. Please try again later.'))
    else:
        form = PasswordResetInitForm()
    return render(req, 'account/generic_account_form.html', {
        'form': form,
        'title': _("Reset your Password - Step 1/3"),
        'primary_action': _("Send Confirmation Email")
        })

@anonymous_required
def reset_password_confirm(req, uuid):
    """
    View to handle Browser account password reset confirmation Requests
    """
    if req.method == 'POST':
        form = PasswordResetFinishForm(req.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if AccountConfirmation.objects.filter(
                    pk=uuid,
                    kind=ACCOUNT_CONFIRMATION_KIND_PASSWORD_RESET).exists():
                pass_conf = AccountConfirmation.objects.get(pk=uuid)
                if pass_conf.confirmed:
                    messages.error(req, _("Link already used!"))
                    return redirect(reverse('account-login'))
                if pass_conf.is_expired:
                    messages.error(req, _("Link expired!"))
                    return redirect(reverse('account-login'))
                if AccountController.change_password(
                        email=pass_conf.user.email,
                        password=password,
                        reset=True):
                    # invalidate confirmation
                    pass_conf.confirmed = True
                    pass_conf.save()
                    messages.success(req, _("Account successfully reset!"))
                else:
                    messages.error(req, _("Failed to reset Password. Please try again later."))
            else:
                raise Http404
            return redirect(reverse('account-login'))
    else:
        form = PasswordResetFinishForm()
    return render(req, 'account/generic_account_form.html', {
        'form': form,
        'title': _("Reset your Password - Step 3/3"),
        'primary_action': _("Reset your Password")
        })

@anonymous_required
@require_GET
def confirmation_resend(req, email):
    """
    View to handle Browser account confirmation resend Requests
    """
    users = User.objects.filter(
        email=email, is_active=False)
    if users.exists():
        user = users[0]
        if AccountController.resend_confirmation(user):
            messages.success(req, _("Successfully resent confirmation email"))
        else:
            messages.error(req, _("Failed to resend confirmation email"))
        return redirect(reverse('account-login'))
    raise Http404
