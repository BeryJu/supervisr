"""Supervisr DNS URLs"""

from django.conf.urls import url

from supervisr.core.utils.constants import UUID_REGEX
from supervisr.dns.views import migrate, records, zones

urlpatterns = [
    # Zones
    url(r'^zones/$', zones.ZoneIndexView.as_view(), name='index'),
    url(r'^zones/create/$', zones.ZoneNewView.as_view(), name='zone-create'),
    url(r'^zones/(?P<uuid>%s)/update/$' % UUID_REGEX,
        zones.ZoneUpdateView.as_view(), name='zone-update'),
    url(r'^zones/(?P<uuid>%s)/delete/$' % UUID_REGEX,
        zones.ZoneDeleteView.as_view(), name='zone-delete'),
    url(r'^zones/(?P<uuid>%s)/records/$' % UUID_REGEX,
        zones.RecordIndexView.as_view(), name='record-list'),
    url(r'^zones/(?P<uuid>%s)/graph/$' % UUID_REGEX,
        zones.ZoneGraphView.as_view(), name='zone-graph'),
    url(r'^migrate/import/bind/$',
        migrate.BindZoneImportWizard.as_view(), name='migrate-import-bind'),
    # Reverse Zones
    url(r'^zones/reverse/$',
        zones.ReverseZoneIndexView.as_view(), name='reverse-zone-index'),
    # Records
    url(r'^records/data/create/$',
        records.DataRecordWizard.as_view(), name='record-data-create'),
    url(r'^records/set/create/$',
        records.SetRecordWizard.as_view(), name='record-set-create'),
    url(r'^records/set/(?P<uuid>%s)/$' % UUID_REGEX,
        records.SetRecordView.as_view(), name='record-set-view'),
    url(r'^records/(?P<uuid>%s)/update/$' % UUID_REGEX,
        records.RecordUpdateView.as_view(), name='record-update'),
    url(r'^records/(?P<uuid>%s)/delete/$' % UUID_REGEX,
        records.RecordDeleteView.as_view(), name='record-delete'),
]
