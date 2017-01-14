import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_GET

from ..controllers import AccountController
from ..decorators import anonymous_required
from ..forms.account import *
from ..ldap_connector import LDAPConnector
from ..models import AccountConfirmation

logger = logging.getLogger(__name__)

@anonymous_required
def login(req):
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
                logger.info("Successfully logged in %s" % form.cleaned_data.get('email'))
                return redirect(reverse('common-index'))
            else:
                # Check if the user's account is pending
                # and inform that, they need to check their emails
                user = User.objects.filter(username=form.cleaned_data.get('email'))
                if user.exists():
                    ac = AccountConfirmation.objects.get(user=user[0])
                    if not ac.confirmed:
                        messages.error(req, _('Account not confirmed yet. Check your emails.'))
                else:
                    messages.error(req, _("Invalid Login"))
                    logger.info("Failed to log in %s" % form.cleaned_data.get('email'))
                return redirect(reverse('account-login'))
    else:
        form = LoginForm()
    return render(req, 'account/login.html', { 'form': form })

@anonymous_required
def signup(req):
    if req.method == 'POST':
        form = SignupForm(req.POST)
        if form.is_valid():
            # Create user
            if not AccountController.signup(
                email=form.cleaned_data.get('email'),
                name=form.cleaned_data.get('name'),
                password=form.cleaned_data.get('password')):
                return redirect(reverse('account-login'))
            messages.success(req, _("Successfully signed up!"))
            logger.info("Successfully signed up %s" % \
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
    django_logout(req)
    messages.success(req, _("Successfully logged out!"))
    return redirect(reverse('common-index'))

@anonymous_required
@require_GET
def confirm(req, uuid):
    if AccountConfirmation.objects.filter(pk=uuid).exists():
        ac = AccountConfirmation.objects.get(pk=uuid)
        if ac.confirmed:
            messages.error(req, _("Account already confirmed!"))
            return redirect(reverse('account-login'))
        if ac.is_expired:
            messages.error(req, _("Confirmation expired"))
            return redirect(reverse('account-login'))
        # activate django user
        ac.user.is_active = True
        ac.user.save()
        # activate LDAP user
        if LDAPConnector.enabled():
            ldap = LDAPConnector()
            ldap.enable_user(ac.user.email)
        # invalidate confirmation
        ac.confirmed = True
        ac.save()
        messages.success(req, _("Account successfully activated!"))
    else:
        raise Http404
    return redirect(reverse('account-login'))

@anonymous_required
def reset_password_init(req):
    if req.method == 'POST':
        form = PasswordResetInitForm(req.POST)
        if form.is_valid():
            pc = AccountConfirmation.objects.create(
                user=req.user,
                kind=ACCOUNT_CONFIRMATION_KIND_PASSWORD_RESET)
            if Mailer.send_password_reset_confirmation(
                req.user.email, pc):
                messages.success(req, _('Reset Link sent successfully'))
            else:
                message.error(req, _('Failed to send Link. Please try again later.'))
    else:
        form = PasswordResetInitForm()
    return render(req, 'account/generic_account_form.html', {
        'form': form,
        'title': _("Reset your Password - Step 1/3"),
        'primary_action': _("Send Confirmation Email")
        })

@anonymous_required
def reset_password_confirm(req, uuid):
    if req.method == 'POST':
        form = PasswordResetFinishForm(req.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if AccountConfirmation.objects.filter(pk=uuid).exists():
                pc = AccountConfirmation.objects.get(pk=uuid)
                if pc.confirmed:
                    messages.error(req, _("Link already used!"))
                    return redirect(reverse('account-login'))
                if pc.is_expired:
                    messages.error(req, _("Link expired!"))
                    return redirect(reverse('account-login'))
                if AccountController.change_password(
                    email=pc.user.email,
                    password=password,
                    reset=True):
                    # invalidate confirmation
                    pc.confirmed = True
                    pc.save()
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
