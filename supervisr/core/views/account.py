"""
Supervisr Core Account Views
"""

import logging
import time

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

from ..decorators import anonymous_required
from ..forms.account import (ChangePasswordForm, LoginForm,
                             PasswordResetFinishForm, PasswordResetInitForm,
                             ReauthForm, SignupForm)
from ..models import AccountConfirmation, UserProfile
from ..signals import (SIG_USER_CHANGE_PASS, SIG_USER_CONFIRM, SIG_USER_LOGIN,
                       SIG_USER_LOGOUT, SIG_USER_PASS_RESET_INIT,
                       SIG_USER_POST_CHANGE_PASS, SIG_USER_POST_SIGN_UP,
                       SIG_USER_RESEND_CONFIRM, SIG_USER_SIGN_UP,
                       SignalException)

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
                # Send event that we're logged in now
                SIG_USER_LOGIN.send(
                    sender=login, user=user, req=req)
                LOGGER.info("Successfully logged in %s", form.cleaned_data.get('email'))
                # Check if there is a next GET parameter and redirect to that
                if 'next' in req.GET:
                    return redirect(req.GET.get('next'))
                # Otherwise just index
                return redirect(reverse('common-index'))
            else:
                # Check if the user's account is pending
                # and inform that, they need to check their emails
                users = User.objects.filter(username=form.cleaned_data.get('email'))
                if users.exists():
                    acc_confs = AccountConfirmation.objects.filter(user=users.first())
                    if acc_confs.exists() and not acc_confs.first().confirmed:
                        # Create url to resend email
                        url = reverse('account-confirmation_resend',
                                      kwargs={'email': users.first().email})
                        messages.error(req, _(('Account not confirmed yet. Check your emails. '
                                               'Click <a href="%(url)s">here</a> to resend the '
                                               'email.')) % {'url': url})
                else:
                    messages.error(req, _("Invalid Login"))
                    LOGGER.info("Failed to log in %s", form.cleaned_data.get('email'))
                return redirect(reverse('account-login'))
    else:
        form = LoginForm()
    return render(req, 'core/generic_form_login.html', {
        'form': form,
        'title': _("SSO - Login"),
        'primary_action': _("Login"),
        'extra_links': {
            'account-signup': 'Sign up for an account',
            'account-reset_password_init': 'Reset your password'
        }
        })

@anonymous_required
def signup(req):
    """
    View to handle Browser Signups Requests
    """
    if req.method == 'POST':
        form = SignupForm(req.POST)
        if form.is_valid():
            # Create user
            new_user = User.objects.create_user(
                username=form.cleaned_data.get('email'),
                email=form.cleaned_data.get('email'),
                first_name=form.cleaned_data.get('name'))
            new_user.save()
            new_user.is_active = False
            new_user.set_password(form.cleaned_data.get('password'))
            new_user.save()
            # Create user profile
            new_up = UserProfile(
                user=new_user,
                news_subscribe=form.cleaned_data.get('news_accept'))
            new_up.save()
            # Send signal for other auth sources
            try:
                SIG_USER_SIGN_UP.send(
                    sender=None,
                    user=new_user,
                    req=req,
                    password=form.cleaned_data.get('password'))
                # Create Account Confirmation UUID
                AccountConfirmation.objects.create(user=new_user)
                # Send event for user creation
                SIG_USER_POST_SIGN_UP.send(
                    sender=None,
                    user=new_user,
                    req=req)
            except SignalException as exception:
                LOGGER.error("Failed to sign up user %s", exception)
                new_up.delete()
                new_user.delete()
                messages.error(req, _("Failed to sign up."))
                return redirect(reverse('account-login'))
            messages.success(req, _("Successfully signed up!"))
            LOGGER.info("Successfully signed up %s",
                        form.cleaned_data.get('email'))
            return redirect(reverse('account-login'))
    else:
        form = SignupForm()
    return render(req, 'core/generic_form_login.html', {
        'form': form,
        'title': _("SSO - Signup"),
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
            # Change Django password
            req.user.set_password(form.cleaned_data.get('password'))
            req.user.save()
            try:
                # Send signal for other auth sources
                SIG_USER_CHANGE_PASS.send(
                    sender=None,
                    user=req.user,
                    req=req,
                    password=form.cleaned_data.get('password'))
                # Trigger Event
                SIG_USER_POST_CHANGE_PASS.send(
                    sender=None,
                    user=req.user,
                    was_reset=False,
                    req=req)
                LOGGER.debug("Successfully updated password for %s", req.user.email)
                messages.success(req, _("Successfully changed password!"))
            except SignalException as exception:
                messages.error(req, _("Failed to change password"))
                LOGGER.error(exception)
            return redirect(reverse('common-index'))
    else:
        form = ChangePasswordForm()
    return render(req, 'core/generic_form_login.html', {
        'form': form,
        'title': _("SSO - Change Password"),
        'primary_action': _("Change Password")
        })

@login_required
@require_GET
def logout(req):
    """
    View to handle Browser logout Requests
    """
    # Send event first because we still have the user
    SIG_USER_LOGOUT.send(
        sender=logout, user=req.user, req=req)
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
            kind=AccountConfirmation.KIND_SIGN_UP).exists():
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
        # Send signal to other auth sources
        SIG_USER_CONFIRM.send(
            sender=None,
            user=acc_conf.user,
            req=req)
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
            AccountConfirmation.objects.create(
                user=user,
                kind=AccountConfirmation.KIND_PASSWORD_RESET)
            SIG_USER_PASS_RESET_INIT.send(
                sender=reset_password_init, user=user)
            messages.success(req, _('Reset Link sent successfully'))
    else:
        form = PasswordResetInitForm()
    return render(req, 'core/generic_form_login.html', {
        'form': form,
        'title': _("SSO - Reset your Password - Step 1/3"),
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
                    kind=AccountConfirmation.KIND_PASSWORD_RESET).exists():
                pass_conf = AccountConfirmation.objects.get(pk=uuid)
                if pass_conf.confirmed:
                    messages.error(req, _("Link already used!"))
                    return redirect(reverse('account-login'))
                if pass_conf.is_expired:
                    messages.error(req, _("Link expired!"))
                    return redirect(reverse('account-login'))
                # Change Django password
                pass_conf.user.set_password(password)
                pass_conf.user.save()
                try:
                    # Send signal for other auth sources
                    SIG_USER_CHANGE_PASS.send(
                        sender=None,
                        user=pass_conf.user,
                        req=req,
                        password=password)
                    # Trigger Event
                    SIG_USER_POST_CHANGE_PASS.send(
                        sender=None,
                        user=pass_conf.user,
                        was_reset=True,
                        req=req)
                    LOGGER.debug("Successfully updated password for %s", req.user.email)
                    messages.success(req, _("Account successfully reset!"))
                    # invalidate confirmation
                    pass_conf.confirmed = True
                    pass_conf.save()
                except SignalException as exception:
                    LOGGER.error(exception)
                    messages.error(req, _("Failed to reset Password. Please try again later."))
            else:
                raise Http404
            return redirect(reverse('account-login'))
    else:
        form = PasswordResetFinishForm()
    return render(req, 'core/generic_form_login.html', {
        'form': form,
        'title': _("SSO - Reset your Password - Step 3/3"),
        'primary_action': _("Reset your Password")
        })

@anonymous_required
@require_GET
def confirmation_resend(req, email):
    """
    View to handle Browser account confirmation resend Requests
    """
    users = User.objects.filter(email=email, is_active=False)
    if users.exists():
        # Invalidate all other links for this user
        old_acs = AccountConfirmation.objects.filter(
            user=users.first())
        for old_ac in old_acs:
            old_ac.confirmed = True
            old_ac.save()
        # Create Account Confirmation UUID
        AccountConfirmation.objects.create(user=users.first())
        SIG_USER_RESEND_CONFIRM.send(
            sender=None,
            user=users.first(),
            req=req)
        messages.success(req, _("Successfully resent confirmation email"))
        return redirect(reverse('account-login'))
    raise Http404

@login_required
def reauth(req):
    """
    Re-authenticate user before important actions
    """
    if req.method == 'POST':
        form = ReauthForm(req.POST)
        if form.is_valid():
            user = authenticate(
                username=req.user.email,
                password=form.cleaned_data.get('password'))
            if user == req.user:
                messages.success(req, _('Successfully Re-Authenticated'))
                req.session['supervisr_require_reauth_done'] = time.time()
                # Check if there is a next GET parameter and redirect to that
                if 'next' in req.GET:
                    return redirect(req.GET.get('next'))
                # Otherwise just index
                return redirect(reverse('common-index'))
        messages.error(req, _('Failed to Re-Authenticate'))
    else:
        form = ReauthForm(initial={'email': req.user.email})

    return render(req, 'core/generic_form_login.html', {
        'form': form,
        'title': _("SSO - Re-Authenticate"),
        'primary_action': _("Login"),
        })
