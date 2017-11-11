"""Supervisr mod beacon Pulse API"""

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
        pul = Pulse.objects.create(**data)
        for mod in modules:
            root = mod.get('module_root')
            matching = PulseModule.objects.filter(module_root=root)
            r_pmod = None
            if not matching.exists():
                r_pmod = PulseModule.objects.create(**mod)
            else:
                r_pmod = matching.first()
            pul.modules.add(r_pmod)
        return {'status': 'ok'}

    @staticmethod
    def init_user_filter(user):
        """This method is used to check if the user has access"""
        return True
