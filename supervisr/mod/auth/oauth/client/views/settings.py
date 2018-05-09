"""
OAuth Client settings
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from supervisr.mod.auth.oauth.client.models import Provider


@login_required
def user_settings(request):
    """Show user settings"""
    provider_state = []
    # pylint: disable=not-an-iterable
    for prov in Provider.objects.all():
        provider_state.append({
            'provider': prov,
            'state': prov.accountaccess_set.filter(user=request.user).exists(),
            'aas': prov.accountaccess_set.filter(user=request.user)
        })
    return render(request, 'mod/auth/oauth/client/settings.html', {
        'provider_state': provider_state,
    })
