"""
Supervisr DNS URLs
"""

from django.conf.urls import url

from supervisr.core.regex import DOMAIN_REGEX
from supervisr.dns.views import core, migrate, zone

urlpatterns = [
    url(r'^$', core.index, name='dns-index'),
    url(r'^zones/$', zone.index, name='dns-zones'),
    url(r'^zones/new/$', zone.ZoneNewView.as_view(), name='dns-zone-new'),
    url(r'^zones/(?P<zone>%s)/edit/$' % DOMAIN_REGEX, zone.edit, name='dns-zone-edit'),
    url(r'^zones/(?P<zone>%s)/delete/$' % DOMAIN_REGEX, zone.delete, name='dns-zone-delete'),
    url(r'^migrate/import/bind/$',
        migrate.BindZoneImportWizard.as_view(), name='migrate-import-bind'),
]
