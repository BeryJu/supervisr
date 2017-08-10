"""
Supervisr DNS URLs
"""

from django.conf.urls import url

from supervisr.core.regex import DOMAIN_REGEX
from supervisr.dns.views import core, migrate, records, zones

urlpatterns = [
    url(r'^$', core.index, name='dns-index'),
    url(r'^zones/$', zones.index, name='dns-zones'),
    url(r'^zones/new/$', zones.ZoneNewView.as_view(), name='dns-zone-new'),
    url(r'^zones/(?P<zone>%s)/edit/$' % DOMAIN_REGEX, zones.edit, name='dns-zone-edit'),
    url(r'^zones/(?P<zone>%s)/delete/$' % DOMAIN_REGEX, zones.delete, name='dns-zone-delete'),
    url(r'^zones/(?P<zone>%s)/records/$' % DOMAIN_REGEX,
        records.list_records, name='dns-record-list'),
    url(r'^migrate/import/bind/$',
        migrate.BindZoneImportWizard.as_view(), name='migrate-import-bind'),
]
