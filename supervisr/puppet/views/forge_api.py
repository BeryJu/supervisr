"""
Supervisr Puppet Forge API views
"""

import logging
from wsgiref.util import FileWrapper

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render

from supervisr.core.models import Setting
from supervisr.puppet.models import PuppetModule, PuppetModuleRelease

LOGGER = logging.getLogger(__name__)


# pylint: disable=unused-argument
def module_list(req):
    """
    Return a list of modules
    """
    return HttpResponse('Not Implemented yet!', status=501)

# pylint: disable=unused-argument
def module(req, user, module):
    """
    Return information about module <module>
    """
    users = User.objects.filter(username=user)
    if not users.exists():
        raise Http404
    r_user = users.first()

    modules = PuppetModule.objects.filter(name=module, owner=r_user)
    if not modules.exists():
        raise Http404
    r_module = modules.first()

    releases = PuppetModuleRelease.objects.filter(module=r_module).order_by('-pk')

    return render(req, 'puppet/api/module.json', {
        'module': r_module,
        'lrel': releases.first(),
        'releases': releases
        }, content_type='application/json')

# pylint: disable=unused-argument
def user_list(req):
    """
    Return user list
    """
    return HttpResponse('Not Implemented yet!', status=501)

# pylint: disable=unused-argument
def user(req, user):
    """
    Return user information
    """
    return HttpResponse('Not Implemented yet!', status=501)

def release_list(req):
    """
    Return a list of releases
    """
    query = Q()
    if 'module' in req.GET:
        # Filter differently if it's name-module or just module
        if '-' in req.GET.get('module'):
            query = query & Q(module__name__icontains=req.GET.get('module').split('-')[1])
        else:
            query = query & Q(module__name__icontains=req.GET.get('module'))

    releases = PuppetModuleRelease.objects.filter(query)

    return render(req, 'puppet/api/release_list.json', {
        'releases': releases
        }, content_type='application/json')

# pylint: disable=unused-argument
def release(req, user, module, version):
    """
    Return list of releases for module
    """
    users = User.objects.filter(username=user)
    if not users.exists():
        raise Http404
    r_user = users.first()

    modules = PuppetModule.objects.filter(name=module, owner=r_user)
    if not modules.exists():
        raise Http404
    r_module = modules.first()

    releases = PuppetModuleRelease.objects.filter(module=r_module, version=version)
    if not releases.exists():
        raise Http404
    r_rel = releases.first()

    return render(req, 'puppet/api/release.json', {
        'release': r_rel
        }, content_type='application/json')

def file(req, user, module, version):
    """
    Return file for release
    """
    if not req.META['HTTP_USER_AGENT'] == Setting.get('allowed_user_agent') and not settings.DEBUG:
        LOGGER.warning("Denied Download with User-Agent '%s'", req.META['HTTP_USER_AGENT'])
        raise Http404
    p_user = User.objects.get(username=user)
    p_module = PuppetModule.objects.get(name=module, owner=p_user)
    p_release = PuppetModuleRelease.objects.get(module=p_module, version=version)

    # generate the file
    filename = "%s-%s-%s.tgz" % (p_user.username, p_module.name, p_release.version)
    response = HttpResponse(FileWrapper(p_release.release), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    p_release.downloads += 1
    p_release.save()

    p_module.downloads += 1
    p_module.save()
    return response
