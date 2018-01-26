"""
Supervisr Bacula URLs
"""
from django.conf.urls import url

from supervisr.mod.contrib.bacula.views import core

urlpatterns = [
    url(r'^$', core.index, name='index'),
    url(r'^volumes/$', core.volumes, name='volumes'),
    url(r'^job/$', core.jobs, name='jobs'),
    url(r'^job/(?P<jobid>\d+)/logs/$', core.job_log, name='job-log'),
    url(r'^job/(?P<jobid>\d+)/files/$', core.job_file, name='job-file'),
    url(r'^settings/$', core.BaculaSettings.as_view(), name='settings'),
]
