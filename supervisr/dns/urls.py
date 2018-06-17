"""Supervisr DNS URLs"""

from django.conf.urls import url
from supervisr.core.regex import DOMAIN_REGEX, UUID_REGEX
from supervisr.dns.views import migrate, records, resource, resourcesets, zones

urlpatterns = [
    url(r'^zones/$', zones.ZoneIndexView.as_view(), name='index'),
    url(r'^zones/create/$', zones.ZoneNewView.as_view(), name='zone-create'),
    url(r'^zones/(?P<zone>%s)/update/$' % DOMAIN_REGEX,
        zones.ZoneUpdateView.as_view(), name='zone-update'),
    url(r'^zones/(?P<zone>%s)/delete/$' % DOMAIN_REGEX,
        zones.ZoneDeleteView.as_view(), name='zone-delete'),
    url(r'^migrate/import/bind/$',
        migrate.BindZoneImportWizard.as_view(), name='migrate-import-bind'),
    # Records
    url(r'^zones/(?P<zone>%s)/records/$' % DOMAIN_REGEX,
        records.RecordIndexView.as_view(), name='record-list'),
    url(r'^zones/(?P<zone>%s)/records/create/$' % DOMAIN_REGEX,
        records.RecordNewView.as_view(), name='record-create'),
    url(r'^zones/(?P<zone>%s)/records/(?P<record>.+)/(?P<uuid>%s)/update/$' %
        (DOMAIN_REGEX, UUID_REGEX), records.RecordUpdateView.as_view(), name='record-update'),
    url(r'^zones/(?P<zone>%s)/records/(?P<record>.+)/(?P<uuid>%s)/delete/$' %
        (DOMAIN_REGEX, UUID_REGEX), records.RecordDeleteView.as_view(), name='record-delete'),
    # Resource Sets
    url(r'^resource_set/create/$',
        resourcesets.ResourceSetCreateView.as_view(), name='rset-create'),
    url(r'^resource_set/(?P<rset_uuid>%s)/$' % UUID_REGEX,
        resourcesets.ResourceSetReadView.as_view(), name='rset-read'),
    url(r'^resource_set/(?P<rset_uuid>%s)/update/$' % UUID_REGEX,
        resourcesets.ResourceSetUpdateView.as_view(), name='rset-update'),
    url(r'^resource_set/(?P<rset_uuid>%s)/delete/$' % UUID_REGEX,
        resourcesets.ResourceSetDeleteView.as_view(), name='rset-delete'),
    # Resources
    url(r'^resource/(?P<rset_uuid>%s)/create/$' % UUID_REGEX,
        resource.ResourceCreateView.as_view(), name='resource-create'),
    url(r'^resource/(?P<resource_uuid>%s)/update/$' % UUID_REGEX,
        resource.ResourceUpdateView.as_view(), name='resource-update'),
    url(r'^resource/(?P<resource_uuid>%s)/delete/$' % UUID_REGEX,
        resource.ResourceDeleteView.as_view(), name='resource-delete'),
]
