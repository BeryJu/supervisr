"""
Supervisr Mod Contrib Bacula Graphing API
"""

from datetime import timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.http import Http404, JsonResponse
from django.utils import timezone

from supervisr.core.api.base import API
from supervisr.core.utils import check_db_connection
from supervisr.mod.contrib.bacula.models import Job


class GraphAPI(API):
    """Bacula Graph API"""

    ALLOWED_VERBS = {
        'GET': ['job_status', 'stored_bytes'],
    }

    def pre_handler(self, request, handler):
        """
        Check if user is superuser and db connection is working
        """
        if not request.user.is_superuser:
            raise Http404
        if not check_db_connection('bacula'):
            raise Http404

    # pylint: disable=unused-argument
    def job_status(self, request, data):
        """
        Get Job status from last 24h
        """
        yesterday = timezone.now() - timedelta(hours=24)

        # This is a bit of a workaround since django won't let me do StartTime__isnull
        first_id = Job.objects.all().order_by('JobId').exclude(StartTime__lte=yesterday).first()
        if not first_id:
            return JsonResponse({})
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
        return {
            'datasets': [
                {
                    'data': graph_job_status,
                    'backgroundColor': ['#CCCCCC', '#60B515', '#49AFD9', '#F76F6C', '#FF8400']
                }
            ],
            'labels': ['Running', 'Completed', 'Waiting', 'Failed', 'Canceled']
        }

    # pylint: disable=unused-argument
    def stored_bytes(self, request, data):
        """
        Get aggregate size of jobs from last week
        """
        dates = [(timezone.now() - timedelta(days=x)).date() for x in range(0, 7)]
        sizes = []
        for date in dates:
            date_size = Job.objects.filter(StartTime__contains=date).aggregate(Sum('JobBytes'))
            sizes.append(date_size['JobBytes__sum'])
        return {
            'datasets': [
                {
                    'data': sizes,
                    'backgroundColor': '#DDDDDD',
                }
            ],
            'labels': [str(date) for date in dates]
        }
