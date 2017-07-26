"""
Supervisr DNS URLs
"""

from django.conf.urls import url

from supervisr.dns.views import core, migrate, zone

urlpatterns = [
    url(r'^$', core.index, name='dns-index'),
    url(r'^zones/$', zone.index, name='dns-zones'),
    url(r'^zones/new/$', zone.ZoneNewView.as_view(), name='dns-zone-new'),
    url(r'^migrate/import/bind/$',
        migrate.BindZoneImportWizard.as_view(), name='migrate-import-bind'),
]
