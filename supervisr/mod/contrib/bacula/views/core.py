"""
Supervisr Static views
"""

from datetime import timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from supervisr.mod.contrib.bacula.models import (Client, File, Job, Log, Media,
                                                 Pool)
from supervisr.mod.contrib.bacula.utils import db_size, size_human


@login_required
@user_passes_test(lambda u: u.is_superuser)
def index(req):
    """
    Show overview of all bacula
    """
    clients = len(Client.objects.all())
    jobs = len(Job.objects.all())
    total_byes = Job.objects.aggregate(Sum('JobBytes'))['JobBytes__sum']
    total_files = Job.objects.aggregate(Sum('JobFiles'))['JobFiles__sum']
    pools = len(Pool.objects.all())
    volumes = len(Media.objects.all())
    volume_size = Media.objects.aggregate(Sum('VolBytes'))['VolBytes__sum']

    yesterday = timezone.now() - timedelta(hours=24)
    last_week = timezone.now() - timedelta(days=7)
    return render(req, 'mod/contrib/bacula/index.html', {
        'clients': clients,
        'jobs': jobs,
        'total_byes': size_human(total_byes),
        'total_files': total_files,
        'db_size': size_human(db_size()),
        'pools': pools,
        'volumes': volumes,
        'volume_size': size_human(volume_size),
        'date_yesterday': yesterday,
        'date_last_week': last_week,
        })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def jobs(req):
    """
    Return a list of all jobs, paginated
    """
    all_jobs = Job.objects.all().order_by('-JobId')
    paginator = Paginator(all_jobs, 50)

    page = req.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pages = paginator.page(paginator.num_pages)

    return render(req, 'mod/contrib/bacula/jobs.html', {
        'pages': pages,
        })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def job_log(req, jobid):
    """
    Return logs for jobid
    """
    logs = Log.objects.filter(JobId=jobid)
    return render(req, 'mod/contrib/bacula/job_log.html', {
        'title': '%s - Jobs' % jobid,
        'logs': logs,
        'job': Job.objects.get(JobId=jobid),
        })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def job_file(req, jobid):
    """
    Return files for jobid
    """
    files = File.objects.filter(JobId=jobid).order_by('-PathId__Path')
    paginator = Paginator(files, 50)

    page = req.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pages = paginator.page(paginator.num_pages)

    return render(req, 'mod/contrib/bacula/job_file.html', {
        'title': '%s - Files' % jobid,
        'pages': pages,
        'job': Job.objects.get(JobId=jobid),
        })