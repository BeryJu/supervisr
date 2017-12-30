"""Supervisr Beacon sender"""
import importlib
import logging
import platform
import sys
from random import uniform

import requests
from django.conf import settings
from django.forms.models import model_to_dict
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import Domain, Setting, User
from supervisr.core.thread.background import catch_exceptions
from supervisr.mod.beacon.models import Pulse, PulseModule

LOGGER = logging.getLogger(__name__)

class Sender(object):
    """Class that sends anonymized"""

    _enabled = True
    _endpoint = ''
    _pulse = None
    _modules = []
    _smear_amount = 0

    def __init__(self):
        self._enabled = getattr(settings, 'BEACON_ENABLED', True)
        self._endpoint = getattr(settings, 'BEACON_REMOTE', '')
        self._install_id = Setting.get('install_id', namespace='supervisr.core')
        self._smear_amount = uniform(0.5, 1.5) # Smear between 0.5 and 1.5
        self._pulse = Pulse(
            install_id=self._install_id,
        )
        self._collect_fixed()
        self._collect_modules()

    def _collect_fixed(self):
        """Collect data which doesn't change, like Python Version and OS Uname"""
        # Collect python version
        self._pulse.python_version = sys.version
        # Collect OS Uname
        self._pulse.os_uname = str(platform.uname())

    def _collect_count(self):
        """Collect Counts of user and domains, and smear them some"""
        self._pulse.domain_count = int(len(Domain.objects.all()) * self._smear_amount)
        self._pulse.user_count = int(len(User.objects.all()) * self._smear_amount)

    def _collect_modules(self):
        """Collect info about modules"""
        for _mod in settings.INSTALLED_APPS:
            if not _mod.startswith('supervisr.'):
                continue
            mod_base = '.'.join(_mod.split('.')[:-2])
            if importlib.util.find_spec(mod_base) is not None:
                LOGGER.debug("Loaded %s", mod_base)
                base = importlib.import_module(mod_base)
                pmod = PulseModule(
                    module_root=mod_base,
                )
                for key, new_key in {
                        '__ui_name__': 'name',
                        '__author__': 'author',
                        '__email__': 'author_email',
                    }.items():
                    value = getattr(base, key, _('Undefined'))
                    setattr(pmod, new_key, value)
                self._modules += [pmod]

    def bundle(self) -> dict:
        """Bundle Pulse instance into json string"""
        pu_dict = model_to_dict(self._pulse)
        mods = []
        for mod in self._modules:
            mods.append(model_to_dict(mod))
        pu_dict['modules'] = mods
        return pu_dict

    def send(self, data):
        """Send json string to endpoint"""
        endpoint = self._endpoint + \
            reverse('supervisr/mod/beacon/api/v1:pulse',
                    kwargs={'verb': 'send'})
        req = requests.post(endpoint, json=data)
        result = req.json()
        if 'code' in result and result.get('code') == 200:
            LOGGER.debug("Successfully pulsed beacon")
        else:
            LOGGER.debug("Failed to pulse: %r", result)

    @catch_exceptions()
    def tick(self):
        """This method is called by supervisr.core.thread.background.BackgroundThread."""
        self._collect_count()
        self.send(self.bundle())
