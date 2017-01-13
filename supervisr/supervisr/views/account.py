import logging
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from ..controllers import *
from ..decorators import anonymous_required
from ..forms.account import AuthenticationForm, ChangePasswordForm, SignupForm
from ..ldap_connector import LDAPConnector
from ..models import AccountConfirmation

logger = logging.getLogger(__name__)

@anonymous_required
def login(req):
    if req.method == 'POST':
        form = AuthenticationForm(req.POST)
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
                user = User.objects.get(username=form.cleaned_data.get('email'))
                ac = AccountConfirmation.objects.get(user=user)
                if not ac.confirmed:
                    messages.error(req, _('Account not confirmed yet. Check your emails.'))
                else:
                    messages.error(req, _("Invalid Login"))
                    logger.info("Failed to log in %s" % form.cleaned_data.get('email'))
                return redirect(reverse('account-login'))
    else:
        form = AuthenticationForm()
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
            logger.info("Successfully signed up %s" % \
                form.cleaned_data.get('email'))
            return redirect(reverse('account-login'))
    else:
        form = SignupForm()
    return render(req, 'account/signup.html', { 'form': form })

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
    return render(req, 'account/change_password.html', { 'form': form })

@login_required
def logout(req):
    django_logout(req)
    messages.success(req, _("Successfully logged out!"))
    return redirect(reverse('common-index'))

@anonymous_required
def confirm(req, uuid):
    current_time = time.time()
    if AccountConfirmation.objects.filter(pk=uuid).exists():
        ac = AccountConfirmation.objects.get(pk=uuid)
        if ac.confirmed:
            messages.error(req, _("Account already confirmed!"))
            return redirect(reverse('account-login'))
        if not ac.is_expired():
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
        messages.error(req, _("Confirmation not found"))
    return redirect(reverse('account-login'))
