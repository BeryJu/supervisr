"""
Supervisr DNS URLs
"""

from django.conf.urls import url

from supervisr.dns.views import core, domain, migrate

urlpatterns = [
    url(r'^$', core.index, name='dns-index'),
    url(r'^domains/$', domain.index, name='dns-domains'),
    url(r'^migrate/import/bind/$',
        migrate.BindZoneImportWizard.as_view(), name='migrate-import-bind'),
]
