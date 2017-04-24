"""
Supervisr Puppet views
"""

from wsgiref.util import FileWrapper

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .builder import ReleaseBuilder
from .models import PuppetModule, PuppetModuleRelease


# pylint: disable=unused-argument
def module_list(req):
    """
    Return a list of modules
    """
    pass

# pylint: disable=unused-argument
def module(req, user, module):
    """
    Return information about module <module>
    """
    pass

# pylint: disable=unused-argument
def user_list(req):
    """
    Return user list
    """
    pass

# pylint: disable=unused-argument
def user(req, user):
    """
    Return user information
    """
    pass

# pylint: disable=unused-argument
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

    return render(req, 'release_list.json.djt', {
        'releases': releases
        }, content_type='application/json')

# pylint: disable=unused-argument
def release(req, user, module, version):
    """
    Return list of releases for module
    """
    pass

# pylint: disable=unused-argument
def file(req, user, module, version):
    """
    Return file for release
    """
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
    return redirect(reverse('admin-debug'))
