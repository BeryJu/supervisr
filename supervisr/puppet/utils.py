"""Supervisr Puppet Utils"""

import json
import logging
import os
import shutil

import requests
from django.conf import settings
from django.core.files import File

from supervisr.core.celery import CELERY_APP
from supervisr.core.models import User
from supervisr.core.tasks import SupervisrTask
from supervisr.puppet.models import PuppetModule, PuppetModuleRelease

LOGGER = logging.getLogger(__name__)


class ForgeImporter(SupervisrTask):
    """Helper class to import users, modules and releases from PuppetForge"""

    name = 'supervisr.puppet.utils.ForgeImporter'
    BASE_URL = 'https://forgeapi.puppetlabs.com'
    output_base = os.path.join(settings.MEDIA_ROOT, 'puppet', 'modules')

    def __init__(self):
        super(ForgeImporter, self).__init__()
        if settings.TEST:
            self.output_base = os.path.join(self.output_base, 'test')
        os.makedirs(self.output_base, exist_ok=True)

    def run(self, *args, **kwargs):
        """Wrapper for import_module"""
        return self.import_module(*args, **kwargs)

    def import_module(self, name):
        """Import user, module and all releases of that module"""
        user, module = name.split('-')
        p_user = self.get_user_info(user)
        p_module = self.get_module_info(p_user, module)
        self.import_releases(p_user, p_module)

    def __get_helper(self, url):
        """Shortcut to get json data"""
        f_url = '%s/%s' % (self.BASE_URL, url)
        LOGGER.debug("About to GET %s", f_url)
        return requests.get(f_url).json()

    def get_user_info(self, username):
        """Get user information and create in DB if non existant"""
        result = self.__get_helper('/v3/users/' + username)

        existing_user = User.objects.filter(
            username=result['username'],
            first_name=result['display_name'])

        if not existing_user:
            LOGGER.debug("Created user '%s' from PuppetForge...", result['username'])
            return User.objects.create(
                username=result['username'],
                first_name=result['display_name'])

        LOGGER.debug("User '%s' exists already", result['username'])
        return existing_user.first()

    def get_module_info(self, user, modulename):
        """Get module information and create in DB if non existant"""
        result = self.__get_helper('/v3/modules/%s-%s' % (user.username, modulename))

        existing_module = PuppetModule.objects.filter(
            owner=user,
            name=result['name'])

        if not existing_module:
            LOGGER.debug("Created module '%s-%s' from PuppetForge...",
                         user.username, result['name'])
            return PuppetModule.objects.create(
                owner=user,
                name=result['name'],
                supported=result['supported'])

        LOGGER.debug("Module '%s-%s' exists already", user.username, result['name'])
        return existing_module.first()

    def import_releases(self, user, module):
        """Get release information and create in DB if non existant"""
        result = self.__get_helper('/v3/releases?module=%s-%s' % (user.username, module.name))

        for release in result['results']:
            existing_module = PuppetModuleRelease.objects.filter(
                module=module,
                version=release['version'])

            if not existing_module:
                LOGGER.debug("Created release '%s-%s@%s' from PuppetForge...",
                             user.username, module.name, release['version'])

                archive = requests.get(self.BASE_URL + release['file_uri'], stream=True)
                filename = '%s/%s-%s-%s.tgz' \
                           % (self.output_base, user.username, module.name, release['version'])
                with open(filename, 'wb') as file:
                    archive.raw.decode_content = True
                    shutil.copyfileobj(archive.raw, file)

                PuppetModuleRelease.objects.create(
                    module=module,
                    version=release['version'],
                    metadata=json.dumps(release['metadata']),
                    readme=release['readme'],
                    changelog=release['changelog'],
                    license=release['license'],
                    release=File(open(filename, mode='rb'))
                )

                os.remove(filename)
            else:
                LOGGER.debug("Release %s-%s@%s exists already", user.username,
                             module.name, release['version'])


CELERY_APP.tasks.register(ForgeImporter())
