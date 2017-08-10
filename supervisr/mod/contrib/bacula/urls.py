"""
Supervisr Bacula URLs
"""
from django.conf.urls import url

from supervisr.mod.contrib.bacula.views import ajax, core

urlpatterns = [
    url(r'^$', core.index, name='bacula-index'),
    url(r'^ajax/graph/job_status\.json$', ajax.ajax_graph_job_status,
        name='bacula-ajax_graph_job_status'),
    url(r'^ajax/graph/stored_bytes\.json$', ajax.ajax_graph_stored_bytes,
        name='bacula-ajax_graph_stored_bytes'),
    url(r'^volumes/$', core.volumes, name='bacula-volumes'),
    url(r'^job/$', core.jobs, name='bacula-jobs'),
    url(r'^job/(?P<jobid>\d+)/logs/$', core.job_log, name='bacula-job-log'),
    url(r'^job/(?P<jobid>\d+)/files/$', core.job_file, name='bacula-job-file'),
]
