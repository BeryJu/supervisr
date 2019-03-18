"""Supervisr Puppet Admin views"""

import traceback

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from supervisr.puppet.builder import ReleaseBuilder
from supervisr.puppet.models import PuppetModule, PuppetModuleRelease


@login_required
@user_passes_test(lambda u: u.is_superuser)
def index(request: HttpRequest) -> HttpResponse:
    """Admin index"""
    module_count = len(PuppetModule.objects.all())
    download_count = PuppetModuleRelease.objects.all().aggregate(Sum('downloads'))
    versions = {}
    for mod in PuppetModule.objects.all():
        latest_releases = PuppetModuleRelease.objects \
            .filter(module=mod) \
            .order_by('-pk')
        if latest_releases.exists():
            versions[mod] = latest_releases.first()
    return render(request, 'puppet/index.html', {
        'module_count': module_count,
        'versions': versions,
        'download_count': download_count['downloads__sum'],
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def debug_build(request: HttpRequest, user: str, module: str) -> HttpResponse:
    """Run Puppet Build"""
    p_users = User.objects.filter(username=user)
    if not p_users.exists():
        raise Http404
    p_user = p_users.first()
    p_modules = PuppetModule.objects.filter(name=module, owner=p_user)
    if not p_modules.exists():
        raise Http404
    p_module = p_modules.first()
    rel_builder = ReleaseBuilder()
    rel_builder.set_module(p_module)
    task = rel_builder.delay()
    messages.success(request, 'Successfully started build: %s' % task.id)
    return redirect(reverse('supervisr_puppet:index'))


@login_required
@user_passes_test(lambda u: u.is_superuser)
def debug_render(request: HttpRequest) -> HttpResponse:
    """Test Render of a template file"""
    ctx = {}
    if request.method == 'POST':

        module = PuppetModule.objects.get(name='supervisr_core')
        builder = ReleaseBuilder()
        builder.set_module(module)
        try:
            rendered = builder.render_template(request.POST.get('templatepath'))
        except Exception:  # pylint: disable=broad-except
            trab = traceback.format_exc()
            rendered = str(trab)
        ctx = {
            'path': request.POST.get('templatepath'),
            'rendered': rendered
        }

    return render(request, 'puppet/debug_render.html', ctx)
