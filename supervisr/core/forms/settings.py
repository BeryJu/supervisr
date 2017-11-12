"""supervisr settings form"""

from django import forms
from django.utils.translation import ugettext as _

from supervisr.core.models import Setting

class SettingsForm(forms.Form):
    """Form to easily edit settings"""

    namespace = ''
    settings = []
    widgets = {}
    _set_objects = {}

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self._validate_settings()
        self._make_widgets()

    def _validate_settings(self):
        """Make sure all settings can be found"""
        for setting in self.settings:
            namespace = self.namespace
            key = setting
            if '/' in setting:
                # Namespace explicitly stated in setting
                namespace, key = setting.split('/')
            matching = Setting.objects.filter(namespace=namespace, key=key)
            if not matching.exists():
                raise ValueError("Setting '%s' in namespace '%s' does not exist" %
                                 (key, namespace))
            self._set_objects['%s/%s' % (namespace, key)] = matching.first()

    def _make_widgets(self):
        """Create widgets from settings"""
        for ns_key, setting_obj in self._set_objects.items():
            _ns, key = ns_key.split('/')
            if ns_key in self.widgets:
                self.fields[ns_key] = self.widgets[ns_key]
            elif key in self.widgets:
                self.fields[ns_key] = self.widgets[key]
            else:
                self.fields[ns_key] = forms.CharField()
            # Set initial from DB. This will override the Widget's setting
            if isinstance(self.fields[ns_key], forms.fields.BooleanField):
                self.fields[ns_key].initial = setting_obj.value_bool
            elif isinstance(self.fields[ns_key], forms.fields.IntegerField):
                self.fields[ns_key].initial = setting_obj.value_int
            else:
                self.fields[ns_key].initial = setting_obj.value
            # Set label if not overridden
            if not self.fields[ns_key].label:
                self.fields[ns_key].label = _(key.title())

    def save(self):
        """Save data back to settings"""
        for ns_key, value in self.cleaned_data.items():
            namespace, key = ns_key.split('/')
