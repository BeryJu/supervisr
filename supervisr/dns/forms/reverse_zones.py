"""Supervisr DNS Reverse Zone Forms"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from supervisr.dns.models import ReverseZone
from supervisr.dns.utils import date_to_soa


class ReverseZoneForm(forms.ModelForm):
    """Create/edit ReverseZoneForm"""

    title = _('General Information')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['soa_serial'].initial = date_to_soa()

    class Meta:

        model = ReverseZone
        fields = ['zone_ip', 'netmask', 'providers', 'enabled', 'soa_mname', 'soa_rname',
                  'soa_serial', 'soa_refresh', 'soa_retry', 'soa_expire', 'soa_ttl']
        widgets = {
            'soa_mname': forms.TextInput(),
            'soa_rname': forms.TextInput(),
        }
        labels = {
            'zone_ip': _('Zone IP'),
            'soa_mname': _('SOA MNAME'),
            'soa_rname': _('SOA RNAME'),
            'soa_serial': _('SOA Serial'),
            'soa_refresh': _('SOA Refresh'),
            'soa_retry': _('SOA Retry'),
            'so_expire': _('SOA Expire'),
            'soa_ttl': _('SOA TTL'),
        }
        help_texts = {
            'netmask': _('CIDR Netmask, e.g. 24'),
            'soa_mname': _('Primary master name server.'),
            'soa_rname': _('Responsible person for this Zone.')
        }
