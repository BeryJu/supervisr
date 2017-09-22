"""
Supervisr Static views
"""

from datetime import timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone

from supervisr.mod.contrib.bacula.decorators import check_bacula_db
from supervisr.mod.contrib.bacula.models import Job


@login_required
@user_passes_test(lambda u: u.is_superuser)
@check_bacula_db
# pylint: disable=unused-argument
def ajax_graph_job_status(req):
    """
    Get Job status from last 24h
    """
    yesterday = timezone.now() - timedelta(hours=24)

    # This is a bit of a workaround since django won't let me do StartTime__isnull
    first_id = Job.objects.all().order_by('JobId').exclude(StartTime__lte=yesterday).first()
    graph_job_status_raw = Job.objects.filter(JobId__gte=first_id.JobId).order_by('-JobId')

    def qs_get_count(qs, default=0, **kwargs):
        """
        Get count of QuerySet, otherwise default
        """
        if qs.filter(**kwargs).exists():
            return qs.filter(**kwargs).count()
        return default

    graph_job_status = [
        qs_get_count(graph_job_status_raw, JobStatus='R'), #Running
        qs_get_count(graph_job_status_raw, JobStatus='T'), #Completed
        qs_get_count(graph_job_status_raw, JobStatus__in=
                     ['B', 'F', 'S', 'm', 'M', 's', 'j', 'c', 'd', 't', 'p', 'C']), #Waiting
        qs_get_count(graph_job_status_raw, JobStatus='f'), #Failed
        qs_get_count(graph_job_status_raw, JobStatus='A'), #Canceled
    ]
    return JsonResponse({
        'datasets': [
            {
                'data': graph_job_status,
                'backgroundColor': ['#CCCCCC', '#60B515', '#49AFD9', '#F76F6C', '#FF8400']
            }
        ],
        'labels': ['Running', 'Completed', 'Waiting', 'Failed', 'Canceled']
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
@check_bacula_db
# pylint: disable=unused-argument
def ajax_graph_stored_bytes(req):
    """
    Get aggregate size of jobs from last week
    """
    dates = [(timezone.now() - timedelta(days=x)).date() for x in range(0, 7)]
    sizes = []
    for date in dates:
        date_size = Job.objects.filter(StartTime__contains=date).aggregate(Sum('JobBytes'))
        sizes.append(date_size['JobBytes__sum'])
    return JsonResponse({
        'datasets': [
            {
                'data': sizes,
                'backgroundColor': '#DDDDDD',
            }
        ],
        'labels': [str(date) for date in dates]
    })
