"""
Supervisr DNS URLs
"""

from django.conf.urls import url

from supervisr.core.regex import DOMAIN_REGEX, UUID_REGEX
from supervisr.dns.views import migrate, records, zones

urlpatterns = [
    url(r'^zones/$', zones.index, name='dns-index'),
    url(r'^zones/new/$', zones.ZoneNewView.as_view(), name='dns-zone-new'),
    url(r'^zones/(?P<zone>%s)/edit/$' % DOMAIN_REGEX, zones.edit, name='dns-zone-edit'),
    url(r'^zones/(?P<zone>%s)/delete/$' % DOMAIN_REGEX, zones.delete, name='dns-zone-delete'),
    url(r'^zones/(?P<zone>%s)/records/$' % DOMAIN_REGEX,
        records.list_records, name='dns-record-list'),
    url(r'^zones/(?P<zone>%s)/records/new/$' % DOMAIN_REGEX, records.RecordNewView.as_view(),
        name='dns-record-new'),
    url(r'^zones/(?P<zone>%s)/records/(?P<record>.+)/(?P<uuid>%s)/edit/$' %
        (DOMAIN_REGEX, UUID_REGEX), records.edit, name='dns-record-edit'),
    url(r'^zones/(?P<zone>%s)/records/(?P<record>.+)/(?P<uuid>%s)/delete/$' %
        (DOMAIN_REGEX, UUID_REGEX), records.delete, name='dns-record-delete'),
    url(r'^migrate/import/bind/$',
        migrate.BindZoneImportWizard.as_view(), name='migrate-import-bind'),
]
