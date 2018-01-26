"""
Supervisr Static views
"""

from datetime import timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from supervisr.core.views.settings import GenericSettingView
from supervisr.mod.contrib.bacula.decorators import check_bacula_db
from supervisr.mod.contrib.bacula.forms.filter import (BaculaSettingsForm,
                                                       JobFilterForm)
from supervisr.mod.contrib.bacula.models import (Client, File, Job, Log, Media,
                                                 Pool)
from supervisr.mod.contrib.bacula.utils import db_size, size_human


@login_required
@user_passes_test(lambda u: u.is_superuser)
@check_bacula_db
def index(request: HttpRequest) -> HttpResponse:
    """Show overview of all bacula"""
    clients = len(Client.objects.all())
    jobs = len(Job.objects.all())
    total_byes = Job.objects.aggregate(Sum('JobBytes'))['JobBytes__sum']
    total_files = Job.objects.aggregate(Sum('JobFiles'))['JobFiles__sum']
    pools = len(Pool.objects.all())
    volumes = len(Media.objects.all())
    volume_size = Media.objects.aggregate(Sum('VolBytes'))['VolBytes__sum']

    yesterday = timezone.now() - timedelta(hours=24)
    last_week = timezone.now() - timedelta(days=7)
    return render(request, 'mod/contrib/bacula/index.html', {
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
@check_bacula_db
def jobs(request: HttpRequest) -> HttpResponse:
    """Return a list of all jobs, paginated"""
    filter_form = JobFilterForm(request.GET)
    query = Q()

    if filter_form.is_valid():
        if filter_form.cleaned_data.get('client', None):
            query = query & Q(ClientId=filter_form.cleaned_data.get('client'))
        if filter_form.cleaned_data.get('level', None):
            query = query & Q(Level=filter_form.cleaned_data.get('level'))
        if filter_form.cleaned_data.get('pool', None):
            query = query & Q(Pool=filter_form.cleaned_data.get('pool'))

    all_jobs = Job.objects.filter(query).order_by('-JobId')
    paginator = Paginator(all_jobs, request.user.rows_per_page)

    page = request.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pages = paginator.page(paginator.num_pages)

    return render(request, 'mod/contrib/bacula/jobs.html', {
        'pages': pages,
        'filter_form': filter_form,
        })

@login_required
@user_passes_test(lambda u: u.is_superuser)
@check_bacula_db
def volumes(request: HttpRequest) -> HttpResponse:
    """Return a list of all volumes"""
    all_volumes = Media.objects.all().order_by('-MediaId')
    paginator = Paginator(all_volumes, request.user.rows_per_page)

    page = request.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pages = paginator.page(paginator.num_pages)

    return render(request, 'mod/contrib/bacula/volumes.html', {
        'pages': pages,
        })

@login_required
@user_passes_test(lambda u: u.is_superuser)
@check_bacula_db
def job_log(request: HttpRequest, jobid: int) -> HttpResponse:
    """Return logs for jobid"""
    logs = Log.objects.filter(JobId=jobid)
    return render(request, 'mod/contrib/bacula/job_log.html', {
        'title': '%s - Jobs' % jobid,
        'logs': logs,
        'job': Job.objects.get(JobId=jobid),
        })

@login_required
@user_passes_test(lambda u: u.is_superuser)
@check_bacula_db
def job_file(request: HttpRequest, jobid: int) -> HttpResponse:
    """Return files for jobid"""
    files = File.objects.filter(JobId=jobid).order_by('-PathId__Path')
    paginator = Paginator(files, request.user.rows_per_page)

    page = request.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pages = paginator.page(paginator.num_pages)

    return render(request, 'mod/contrib/bacula/job_file.html', {
        'title': '%s - Files' % jobid,
        'pages': pages,
        'job': Job.objects.get(JobId=jobid),
        })

class BaculaSettings(GenericSettingView):
    """Bacula settings"""

    form = BaculaSettingsForm
    template_name = 'mod/contrib/bacula/settings.html'
