"""Supervisr mod beacon Pulse API"""

from django.db import IntegrityError

from supervisr.core.api.models import ModelAPI
from supervisr.mod.beacon.models import Pulse, PulseModule


class PulseAPI(ModelAPI):
    """Pulse API"""

    model = Pulse
    editable_fields = ['install_id', 'time', 'python_version', 'os_uname',
                       'user_count', 'domain_count', 'modules']

    ALLOWED_VERBS = {
        'POST': ['send'],
    }

    # pylint: disable=unused-argument
    def send(self, request, data):
        """Create pulse with modules from data"""
        modules = data.pop('modules')
        install_id = data.get('install_id')
        pul = Pulse.objects.create(**data)
        try:
            for mod in modules:
                root = mod.get('module_root')
                matching = PulseModule.objects.filter(module_root=root)
                r_pmod = None
                if not matching.exists():
                    r_pmod = PulseModule.objects.create(**mod)
                else:
                    r_pmod = matching.first()
                pul.modules.add(r_pmod)
            for old_pulses in Pulse.objects.filter(install_id=install_id).exclude(pk=pul.pk):
                old_pulses.delete()
        except IntegrityError:
            # Ignore IntegrityError, which happen if the same install sends twice
            # at the same time
            pass
        return {'status': 'ok'}

    @staticmethod
    def init_user_filter(user):
        """This method is used to check if the user has access"""
        return True
