"""
Supervisr Puppet Admin views
"""

import traceback

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import reverse

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
    return render(req, 'puppet/index.html', {
        'module_count': module_count,
        'download_count': download_count['downloads__sum'],
        })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def debug_build(req, user, module):
    """
    Run Puppet Build
    """
    p_user = User.objects.get(username=user)
    p_module = PuppetModule.objects.get(name=module, owner=p_user)
    rel_builder = ReleaseBuilder(p_module)
    rel_builder.build()
    messages.success(req, 'Successfully built %s-%s' % (user, module))
    return redirect(reverse('puppet:puppet-index'))

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