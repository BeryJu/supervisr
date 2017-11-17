"""supervisr settings form"""
from collections import OrderedDict

from django import forms
from django.utils.translation import ugettext as _

from supervisr.core.models import Setting


class SettingsForm(forms.Form):
    """Form to easily edit settings"""

    namespace = ''
    settings = []
    widgets = {}
    _set_objects = {}
    attrs_map = {}

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self._set_objects = self._get_setting_objs()
        self._make_widgets()
        self._apply_attrs_map()

    def _get_setting_objs(self) -> dict:
        """Make sure all settings can be found"""
        objects = OrderedDict()
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
            objects['%s/%s' % (namespace, key)] = matching.first()
        return objects

    def _make_widgets(self):
        """Create widgets from settings"""
        for ns_key, setting_obj in self._set_objects.items():
            _ns, key = ns_key.split('/')
            if ns_key in self.widgets:
                self.fields[ns_key] = self.widgets[ns_key]
            elif key in self.widgets:
                self.fields[ns_key] = self.widgets[key]
            else:
                self.fields[ns_key] = forms.CharField(required=False)
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

    def _apply_attrs_map(self):
        """Apply attributes from self.attrs_map to widgets"""
        for name, attrs in self.attrs_map.items():
            ns_key = '%s/%s' % (self.namespace, name) if '/' not in name else name
            if ns_key in self.fields:
                self.fields[ns_key].attrs = attrs

    def save(self):
        """Save data back to settings"""
        updated_count = 0
        for ns_key, value in self.cleaned_data.items():
            # check if this setting is even meant for us
            if ns_key in self.fields:
                # Only update if needed
                if self._set_objects[ns_key].value != value:
                    print(self._set_objects[ns_key].value)
                    print(value)
                    self._set_objects[ns_key].value = value
                    self._set_objects[ns_key].save()
                    updated_count += 1
        return updated_count
