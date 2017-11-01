"""
Supervisr Puppet Forge API views
"""

import logging
from wsgiref.util import FileWrapper

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse

from supervisr.core.models import Setting
from supervisr.puppet.models import PuppetModule, PuppetModuleRelease

LOGGER = logging.getLogger(__name__)

def check_key(view_function):
    """
    Decorator to check puppet key in url
    """
    def wrap(*args, **kwargs):
        """
        Check if key is the same as in DB
        """
        if 'key' in kwargs:
            set_key = Setting.get('url_key')
            if not set_key == kwargs['key']:
                raise Http404
            del kwargs['key']
        return view_function(*args, **kwargs)

    wrap.__doc__ = view_function.__doc__
    wrap.__name__ = view_function.__name__
    return wrap

@check_key
# pylint: disable=unused-argument
def module_list(req):
    """
    Return a list of modules
    """
    return HttpResponse('Not Implemented yet!', status=501)

@check_key
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

    return JsonResponse(_json_module(r_module))

@check_key
# pylint: disable=unused-argument
def user_list(req):
    """
    Return user list
    """
    return HttpResponse('Not Implemented yet!', status=501)

@check_key
# pylint: disable=unused-argument
def user(req, user):
    """
    Return user information
    """
    return HttpResponse('Not Implemented yet!', status=501)

@check_key
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

    return JsonResponse({
        "pagination": {
            "limit": 20,
            "offset": 0,
            "first": "/",
            "previous": None,
            "current": "/",
            "next": None,
            "total": len(releases)
        },
        "results": _json_release_list(releases)
    })

@check_key
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

    return JsonResponse(_json_release(r_rel))

@check_key
# pylint: disable=unused-argument
def file(req, user, module, version):
    """
    Return file for release
    """
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

# Json helpers
# These methods convert PuppetModules or PuppetModuleReleases into Objects
# which have the same structure as https://forgeapi.puppetlabs.com/

def _json_release(release):
    """Convert a single release"""
    return {
        "uri": reverse('supervisr/puppet:release', kwargs={
            'user': release.module.owner.username,
            'module': release.module.name,
            'version': release.version,
            'key': Setting.get('url_key')
            }),
        "slug": "%s-%s-%s" % (release.module.owner.username, release.module.name, release.version),
        "version": release.version,
        "module": {
            "uri": reverse('supervisr/puppet:module', kwargs={
                'user': release.module.owner.username,
                'module': release.module.name,
                'key': Setting.get('url_key')
                }),
            "slug": "%s-%s" % (release.module.owner.username, release.module.name),
            "name": release.module.name,
            "owner": {
                "url": reverse('supervisr/puppet:user', kwargs={
                    'user': release.module.owner.username,
                    'key': Setting.get('url_key')
                    }),
                "slug": release.module.owner.username,
                "username": release.module.owner.username,
            }
        },
        "metadata": release.get_metaobject,
        "tags": [],
        "supported": release.module.supported,
        "file_size": release.get_size,
        "file_md5": release.get_md5,
        "file_uri": "/v3/files/%s-%s-%s.tar.gz" % (release.module.owner.username, \
                                                   release.module.name, release.version),
        "downloads": release.get_downloads,
        "readme": release.readme,
        "changelog": release.changelog,
        "license": release.license,
        "created_at": release.create_at,
        "updated_at": release.update_at,
    }

def _json_release_list(releases):
    """Create a list of releases"""
    arr = []
    for rel in releases:
        arr.append(_json_release(rel))
    return arr

def _json_module(module):
    """Convert a single module"""
    return {
        "uri": reverse('supervisr/puppet:module', kwargs={
            'user': module.owner.username,
            'module': module.name,
            'key': Setting.get('url_key')
            }),
        "name": module.name,
        "downloads": module.downloads,
        "created_at": module.create_at,
        "updated_at": module.update_at,
        "supported": True,
        "slug": "%s-%s" % (module.owner.username, module.name),
        "owner": {
            "uri": reverse('supervisr/puppet:user', kwargs={
                'user': module.owner.username,
                'key': Setting.get('url_key')
                }),
            "username": module.owner.username
        },
        "current_release": _json_release(module.puppetmodulerelease_set.all() \
                                         .order_by('-pk').first()),
        "releases": _json_release_list(module.puppetmodulerelease_set.all()),
        "homepage_url": "uri",
        "issues_url": "uri"
    }
