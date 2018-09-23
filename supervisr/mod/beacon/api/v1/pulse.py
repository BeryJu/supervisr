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

    def send(self, request, data):
        """Create pulse with modules from data"""
        modules = data.pop('modules')
        install_id = data.pop('install_id')
        pulse = Pulse.objects.get_or_create(
            install_id=install_id,
            defaults=data
        )
        for mod in modules:
            root = mod.get('module_root')
            matching = PulseModule.objects.filter(module_root=root)
            pulse_module = None
            if not matching.exists():
                pulse_module = PulseModule.objects.create(**mod)
            else:
                pulse_module = matching.first()
            pulse.modules.add(pulse_module)
        return {'status': 'ok'}

    @staticmethod
    def init_user_filter(user):
        """This method is used to check if the user has access"""
        return True
