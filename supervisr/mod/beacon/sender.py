"""Supervisr Beacon sender"""
import importlib
import logging
import platform
import sys
from json.decoder import JSONDecodeError
from random import uniform

import requests
from django.conf import settings
from django.forms.models import model_to_dict
from django.urls import reverse
from supervisr.core.models import Domain, Setting, User
from supervisr.core.signals import SIG_SETTING_UPDATE
from supervisr.mod.beacon.models import Pulse, PulseModule

LOGGER = logging.getLogger(__name__)


class Sender(object):
    """Class that sends anonymized"""

    _enabled = True
    _endpoint = ''
    _pulse = None
    _modules = []
    _versions = []
    _smear_amount = 0

    def __init__(self):
        self._enabled = Setting.get_bool('enabled')
        self._endpoint = Setting.get('endpoint')
        self._install_id = Setting.get('install_id', namespace='supervisr.core')
        SIG_SETTING_UPDATE.connect(self.on_setting_update)
        self._smear_amount = uniform(0.5, 1.5)  # Smear between 0.5 and 1.5
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
                # Create module
                pmod = PulseModule(
                    module_root=mod_base,
                )
                for key, new_key in {
                        '__ui_name__': 'name',
                        '__author__': 'author',
                        '__email__': 'author_email',
                }.items():
                    value = getattr(base, key, 'Undefined')
                    setattr(pmod, new_key, value)
                self._modules.append(pmod)

    def bundle(self) -> dict:
        """Bundle Pulse instance into json string"""
        pu_dict = model_to_dict(self._pulse)
        pu_dict['modules'] = [model_to_dict(mod) for mod in self._modules]
        return pu_dict

    def send(self, data):
        """Send json string to endpoint"""
        endpoint = self._endpoint + \
            reverse('supervisr_mod_beacon_api_v1:pulse',
                    kwargs={'verb': 'send'})
        req = requests.post(endpoint, json=data)
        try:
            result = req.json()
            if result['code'] == 200 and result['data']['status'] == 'ok':
                LOGGER.debug("Successfully pulsed beacon")
            else:
                LOGGER.debug("Failed to pulse: %r", result)
        except JSONDecodeError:
            pass

    # pylint: disable=unused-argument
    def on_setting_update(self, sender: Setting, **kwargs):
        """Handle changed settings"""
        if sender.namespace != 'supervisr.mod.beacon':
            return
        if sender.key == 'enabled':
            self._enabled = sender.value_bool
        elif sender.key == 'endpoint':
            self._endpoint = sender.value

    def tick(self):
        """This method is called by celer task in supervisr.mod.beacon.signals."""
        self._collect_count()
        self.send(self.bundle())
