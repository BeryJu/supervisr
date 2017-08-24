"""
Supervisr Core User Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render
from django.utils.translation import ugettext as _

from supervisr.core.forms.user import EditUserForm, FeedbackForm
from supervisr.core.mailer import send_message
from supervisr.core.models import Event


@login_required
def index(req):
    """
    Show index view User informations
    """
    initial_data = {
        'name': req.user.first_name,
        'username': req.user.userprofile.username,
        'email': req.user.email,
        'unix_username': req.user.userprofile.unix_username,
        'unix_userid': req.user.userprofile.unix_userid,
    }
    if req.method == 'POST':
        form = EditUserForm(req.POST, initial=initial_data)
        if form.is_valid():
            req.user.first_name = form.cleaned_data.get('name')
            req.user.save()
            req.user.userprofile.username = form.cleaned_data.get('username')
            req.user.userprofile.save()
            messages.success(req, _('User updated successfully'))
    else:
        form = EditUserForm(initial=initial_data)
    return render(req, 'user/index.html', {'form': form})

@login_required
def events(req):
    """
    Show a paginated list of all events
    """
    event_list = Event.objects.filter(
        user=req.user, hidden=False).order_by('-create_date')
    paginator = Paginator(event_list, 25)

    page = req.GET.get('page')
    try:
        event_page = paginator.page(page)
    except PageNotAnInteger:
        event_page = paginator.page(1)
    except EmptyPage:
        event_page = paginator.page(paginator.num_pages)

    return render(req, 'user/events.html', {'events': event_page})

@login_required
def send_feedback(req):
    """
    Show Form to send feedback
    """
    if req.method == 'POST':
        form = FeedbackForm(req.POST, initial={'email': req.user.email})
        if form.is_valid():
            email = req.user.email
            text = form.cleaned_data.get('text')
            send_message(['jens@beryju.org'], '[Supervisr] Feedback from %s' % email,
                         text='User %s sent feedback: %s' % (email, text))
            messages.success(req, _('Successfully sent feedback.'))

    form = FeedbackForm(initial={'email': req.user.email})
    return render(req, 'user/feedback.html', {
        'title': 'Send Feedback',
        'primary_action': 'Send',
        'form': form
        })
