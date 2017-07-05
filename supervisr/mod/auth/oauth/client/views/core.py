"""
Core Oauth Views
"""

from __future__ import unicode_literals

import base64
import hashlib
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.encoding import force_text, smart_bytes
from django.utils.translation import ugettext as _
from django.views.generic import RedirectView, View

from supervisr.mod.auth.oauth.client.clients import get_client
from supervisr.mod.auth.oauth.client.models import AccountAccess, Provider

LOGGER = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class OAuthClientMixin(object):
    "Mixin for getting OAuth client for a provider."

    client_class = None

    def get_client(self, provider):
        "Get instance of the OAuth client for this provider."
        if self.client_class is not None:
            # pylint: disable=not-callable
            return self.client_class(provider)
        return get_client(provider)


class OAuthRedirect(OAuthClientMixin, RedirectView):
    "Redirect user to OAuth provider to enable access."

    permanent = False
    params = None

    # pylint: disable=unused-argument
    def get_additional_parameters(self, provider):
        "Return additional redirect parameters for this provider."
        return self.params or {}

    # pylint: disable=no-self-use
    def get_callback_url(self, provider):
        "Return the callback url for this provider."
        return reverse('supervisr/mod/auth/oauth/client:oauth-client-callback',
                       kwargs={'provider': provider.name})

    def get_redirect_url(self, **kwargs):
        "Build redirect url for a given provider."
        name = kwargs.get('provider', '')
        try:
            provider = Provider.objects.get(name=name)
        except Provider.DoesNotExist:
            raise Http404('Unknown OAuth provider.')
        else:
            if not provider.enabled():
                raise Http404('Provider %s is not enabled.' % name)
            client = self.get_client(provider)
            callback = self.get_callback_url(provider)
            params = self.get_additional_parameters(provider)
            return client.get_redirect_url(self.request, callback=callback, parameters=params)


class OAuthCallback(OAuthClientMixin, View):
    "Base OAuth callback view."

    provider_id = None
    provider = None

    # pylint: disable=unused-argument
    def get(self, request, *args, **kwargs):
        """
        View Get handler
        """
        name = kwargs.get('provider', '')
        try:
            self.provider = Provider.objects.get(name=name)
        except Provider.DoesNotExist:
            raise Http404('Unknown OAuth provider.')
        else:
            if not self.provider.enabled():
                raise Http404('Provider %s is not enabled.' % name)
            client = self.get_client(self.provider)
            callback = self.get_callback_url(self.provider)
            # Fetch access token
            raw_token = client.get_access_token(self.request, callback=callback)
            if raw_token is None:
                return self.handle_login_failure(self.provider, "Could not retrieve token.")
            # Fetch profile info
            info = client.get_profile_info(raw_token)
            if info is None:
                return self.handle_login_failure(self.provider, "Could not retrieve profile.")
            identifier = self.get_user_id(self.provider, info)
            if identifier is None:
                return self.handle_login_failure(self.provider, "Could not determine id.")
            # Get or create access record
            defaults = {
                'access_token': raw_token,
            }
            access, created = AccountAccess.objects.get_or_create(
                provider=self.provider, identifier=identifier, defaults=defaults
            )
            if not created:
                access.access_token = raw_token
                AccountAccess.objects.filter(pk=access.pk).update(**defaults)
            user = authenticate(provider=self.provider, identifier=identifier)
            if user is None:
                return self.handle_new_user(self.provider, access, info)
            return self.handle_existing_user(self.provider, user, access, info)

    # pylint: disable=unused-argument, no-self-use
    def get_callback_url(self, provider):
        "Return callback url if different than the current url."
        return None

    # pylint: disable=unused-argument, no-self-use
    def get_error_redirect(self, provider, reason):
        "Return url to redirect on login failure."
        return settings.LOGIN_URL

    # pylint: disable=unused-argument, no-self-use
    def get_login_redirect(self, provider, user, access, new=False):
        "Return url to redirect authenticated users."
        messages.success(self.request, _("Successfully linked %(provider)s!" % {
            'provider': self.provider.ui_name
            }))
        return 'common-index'

    # pylint: disable=unused-argument, no-self-use
    def get_or_create_user(self, provider, access, info):
        "Create a shell auth.User."
        digest = hashlib.sha1(smart_bytes(access)).digest()
        # Base 64 encode to get below 30 characters
        # Removed padding characters
        username = force_text(base64.urlsafe_b64encode(digest)).replace('=', '')
        # pylint: disable=invalid-name
        User = get_user_model()
        kwargs = {
            User.USERNAME_FIELD: username,
            'email': '',
            'password': None
        }
        return User.objects.create_user(**kwargs)

    # pylint: disable=unused-argument
    def get_user_id(self, provider, info):
        "Return unique identifier from the profile info."
        id_key = self.provider_id or 'id'
        result = info
        try:
            for key in id_key.split('.'):
                result = result[key]
            return result
        except KeyError:
            return None

    # pylint: disable=unused-argument
    def handle_existing_user(self, provider, user, access, info):
        "Login user and redirect."
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect(self.get_login_redirect(provider, user, access))

    def handle_login_failure(self, provider, reason):
        "Message user and redirect on error."
        LOGGER.error('Authenication Failure: %s', reason)
        messages.error(self.request, _('Authenication Failed.'))
        return redirect(self.get_error_redirect(provider, reason))

    def handle_new_user(self, provider, access, info):
        "Create a shell auth.User and redirect."
        user = self.get_or_create_user(provider, access, info)
        access.user = user
        AccountAccess.objects.filter(pk=access.pk).update(user=user)
        user = authenticate(provider=access.provider, identifier=access.identifier)
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect(self.get_login_redirect(provider, user, access, True))

@login_required
def disconnect(req, provider):
    """
    Delete connection with provider
    """
    provider = Provider.objects.filter(name=provider)
    if not provider.exists():
        raise Http404
    r_provider = provider.first()

    aas = AccountAccess.objects.filter(provider=r_provider, user=req.user)
    if not aas.exists():
        raise Http404
    r_aas = aas.first()

    if req.method == 'POST' and 'confirmdelete' in req.POST:
        # User confirmed deletion
        r_aas.delete()
        messages.success(req, _('Connection successfully deleted'))
        return redirect(reverse('supervisr/mod/auth/oauth/client:user_settings'))

    return render(req, 'core/generic_delete.html', {
        'object': 'OAuth Connection with %s' % r_provider.ui_name,
        'delete_url': reverse('supervisr/mod/auth/oauth/client:oauth-client-disconnect', kwargs={
            'provider': r_provider.name,
            })
        })
