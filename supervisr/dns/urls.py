"""Supervisr DNS URLs"""

from django.conf.urls import url

from supervisr.core.regex import DOMAIN_REGEX, UUID_REGEX
from supervisr.dns.views import (migrate, recordresource, records,
                                 resourcesets, zones)

urlpatterns = [
    url(r'^zones/$', zones.index, name='dns-index'),
    url(r'^zones/create/$', zones.ZoneNewView.as_view(), name='zone-create'),
    url(r'^zones/(?P<zone>%s)/update/$' % DOMAIN_REGEX, zones.update, name='zone-update'),
    url(r'^zones/(?P<zone>%s)/delete/$' % DOMAIN_REGEX, zones.delete, name='zone-delete'),
    url(r'^zones/(?P<zone>%s)/records/$' % DOMAIN_REGEX,
        records.list_records, name='dns-record-list'),
    url(r'^migrate/import/bind/$',
        migrate.BindZoneImportWizard.as_view(), name='migrate-import-bind'),
    url(r'^resource_set/create/$',
        resourcesets.ResourceSetCreateView.as_view(), name='rset-create'),
    url(r'^resource_set/(?P<rset_uuid>%s)/$' % UUID_REGEX,
        resourcesets.ResourceSetReadView.as_view(), name='rset-read'),
    url(r'^resource_set/(?P<rset_uuid>%s)/update/$' % UUID_REGEX,
        resourcesets.ResourceSetUpdateView.as_view(), name='rset-update'),
    url(r'^resource_set/(?P<rset_uuid>%s)/delete/$' % UUID_REGEX,
        resourcesets.ResourceSetDeleteView.as_view(), name='rset-delete'),
    # Record Resource
    url(r'^record_resource/new/$',
        recordresource.RecordResourceCreateView.as_view(), name='rres-create'),
    url(r'^record_resource/(?P<rres_uuid>%s)/update/$' % UUID_REGEX,
        recordresource.RecordResourceUpdateView.as_view(), name='rres-update'),
    url(r'^record_resource/(?P<rres_uuid>%s)/delete/$' % UUID_REGEX,
        recordresource.RecordResourceDeleteView.as_view(), name='rres-delete'),
    # Records
    url(r'^zones/(?P<zone>%s)/records/create/$' % DOMAIN_REGEX, records.RecordNewView.as_view(),
        name='dns-record-create'),
    url(r'^zones/(?P<zone>%s)/records/(?P<record>.+)/(?P<uuid>%s)/update/$' %
        (DOMAIN_REGEX, UUID_REGEX), records.update, name='dns-record-update'),
    url(r'^zones/(?P<zone>%s)/records/(?P<record>.+)/(?P<uuid>%s)/delete/$' %
        (DOMAIN_REGEX, UUID_REGEX), records.delete, name='dns-record-delete'),
]
