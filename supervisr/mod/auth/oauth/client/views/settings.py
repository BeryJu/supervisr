"""
OAuth Client settings
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from supervisr.mod.auth.oauth.client.models import Provider


@login_required
def user_settings(req):
    """
    Show user settings
    """
    providers = Provider.objects.all()
    provider_state = []
    for prov in providers:
        provider_state.append({
            'provider': prov,
            'state': prov.accountaccess_set.filter(user=req.user).exists(),
            'aas': prov.accountaccess_set.filter(user=req.user)
            })
    return render(req, 'mod/auth/oauth/client/settings.html', {
        'provider_state': provider_state,
        })
