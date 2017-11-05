"""
Supervisr Puppet Admin views
"""

import traceback

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from supervisr.core.models import get_system_user
from supervisr.puppet.builder import ReleaseBuilder
from supervisr.puppet.models import PuppetModule, PuppetModuleRelease


@login_required
@user_passes_test(lambda u: u.is_superuser)
def index(req):
    """
    Admin index
    """
    module_count = len(PuppetModule.objects.all())
    download_count = PuppetModuleRelease.objects.all().aggregate(Sum('downloads'))
    # Show latest version of internal modules
    supervisr_user = User.objects.get(pk=get_system_user())
    versions = {}
    for mod in PuppetModule.objects.filter(owner=supervisr_user):
        latest_releases = PuppetModuleRelease.objects \
                            .filter(module=mod) \
                            .order_by('-pk')
        if latest_releases.exists():
            versions[mod] = latest_releases.first()
    print(versions)
    return render(req, 'puppet/index.html', {
        'module_count': module_count,
        'versions': versions,
        'download_count': download_count['downloads__sum'],
        })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def debug_build(req, user, module):
    """
    Run Puppet Build
    """
    p_users = User.objects.filter(username=user)
    if not p_users.exists():
        raise Http404
    p_user = p_users.first()
    p_modules = PuppetModule.objects.filter(name=module, owner=p_user)
    if not p_modules.exists():
        raise Http404
    p_module = p_modules.first()
    rel_builder = ReleaseBuilder(p_module)
    rel_builder.build()
    messages.success(req, 'Successfully built %s-%s' % (user, module))
    return redirect(reverse('supervisr/puppet:puppet-index'))

@login_required
@user_passes_test(lambda u: u.is_superuser)
def debug_render(req):
    """
    Test Render of a template file
    """
    ctx = {}
    if req.method == 'POST':

        module = PuppetModule.objects.get(name='supervisr_core')
        builder = ReleaseBuilder(module)
        try:
            rendered = builder.render_template(req.POST.get('templatepath'))
        except Exception: # pylint: disable=broad-except
            trab = traceback.format_exc()
            rendered = str(trab)
        ctx = {
            'path': req.POST.get('templatepath'),
            'rendered': rendered
        }

    return render(req, 'puppet/debug_render.html', ctx)
