"""
Supervisr Puppet Forge API views
"""

import logging
from wsgiref.util import FileWrapper

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
    return HttpResponse('Not Implemented yet!', status=501)

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
    return HttpResponse('Not Implemented yet!', status=501)

def file(req, user, module, version):
    """
    Return file for release
    """
    if not req.META['HTTP_USER_AGENT'] == Setting.get('puppet:allowed_user_agent'):
        LOGGER.warning("Denied Download with User-Agent '%s'", req.META['HTTP_USER_AGENT'])
        raise Http404
    p_user = User.objects.get(username=user)
    p_module = PuppetModule.objects.get(name=module, owner=p_user)
    p_release = PuppetModuleRelease.objects.get(module=p_module, version=version)

    # generate the file
    filename = "%s-%s-%s" % (p_user.username, p_module.name, p_release.version)
    response = HttpResponse(FileWrapper(p_release.release), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    p_release.downloads += 1
    p_release.save()

    p_module.downloads += 1
    p_module.save()
    return response
