"""
Supervisr Core User Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from ..forms.user import EditUserForm
from ..models import Event


@login_required
def index(req):
    """
    Show index view User informations
    """
    initial_data = {
        'name': req.user.first_name,
        'email': req.user.email,
        'unix_username': req.user.userprofile.unix_username,
        'unix_userid': req.user.userprofile.unix_userid,
        'news_accept': req.user.userprofile.news_subscribe,
    }
    if req.method == 'POST':
        form = EditUserForm(req.POST, initial=initial_data)
        if form.is_valid():
            req.user.first_name = form.cleaned_data.get('name')
            req.user.save()
            print(form.cleaned_data.get('news_accept'))
            req.user.userprofile.news_subscribe = form.cleaned_data.get('news_accept')
            req.user.userprofile.save()
            messages.success(req, 'User updated successfully')
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
