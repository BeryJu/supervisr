"""
Supervisr Core User Views
"""

from django.contrib import messages
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views import View

from supervisr.core.decorators import reauth_required
from supervisr.core.forms.users import EditUserForm, FeedbackForm
from supervisr.core.mailer import send_message
from supervisr.core.models import Event, User


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """Show index view User information"""
    initial_data = {
        'name': request.user.first_name,
        'username': request.user.username,
        'email': request.user.email,
        'unix_username': request.user.unix_username,
        'unix_userid': request.user.unix_userid,
        'theme': request.user.theme,
        'rows_per_page': request.user.rows_per_page,
        'api_key': request.user.api_key,
    }
    if request.method == 'POST':
        form = EditUserForm(request.POST, initial=initial_data)
        if form.is_valid():
            request.user.first_name = form.cleaned_data.get('name')
            request.user.email = form.cleaned_data.get('email')
            request.user.username = form.cleaned_data.get('username')
            request.user.theme = form.cleaned_data.get('theme')
            request.user.rows_per_page = form.cleaned_data.get('rows_per_page')
            request.user.save()
            messages.success(request, _('User updated successfully'))
    else:
        form = EditUserForm(initial=initial_data)
    return render(request, 'user/index.html', {'form': form})


@login_required
def events(request: HttpRequest) -> HttpResponse:
    """Show a paginated list of all events"""
    event_list = Event.objects.filter(
        user=request.user, hidden=False).order_by('-create_date')
    paginator = Paginator(event_list, request.user.rows_per_page)

    page = request.GET.get('page')
    try:
        event_page = paginator.page(page)
    except PageNotAnInteger:
        event_page = paginator.page(1)
    except EmptyPage:
        event_page = paginator.page(paginator.num_pages)

    return render(request, 'user/events.html', {'events': event_page})


@login_required
def send_feedback(request: HttpRequest) -> HttpResponse:
    """Show Form to send feedback"""
    if request.method == 'POST':
        form = FeedbackForm(request.POST, initial={'email': request.user.email})
        if form.is_valid():
            email = request.user.email
            text = form.cleaned_data.get('message')
            send_message.delay(
                recipients=['support@beryju.org', 'admin@beryju.org'],
                subject='[supervisr] Feedback from %s' % email,
                text='User %s sent feedback: %s' % (email, text))
            messages.success(request, _('Successfully sent feedback.'))

    form = FeedbackForm(initial={'email': request.user.email})
    return render(request, 'user/feedback.html', {
        'title': 'Send Feedback',
        'primary_action': 'Send',
        'form': form
    })


@method_decorator(login_required, name='dispatch')
@method_decorator(reauth_required, name='dispatch')
class UserDeleteView(View):
    """View to allow users to delete their own profile"""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Handle get request

        Args:
            request: The Current HttpRequest

        Returns:
            Rendered HTML
        """
        return render(request, 'core/generic_delete.html', {
            'object': 'Account %s' % request.user.username,
            'title': 'Delete %s' % request.user.username,
            'delete_url': reverse('user-delete'),
            'extra_markup': '<h4>%s</h4>' % _('This action cannot be reversed!')
        })

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handle post request

        Args:
            request: The Current HttpRequest

        Returns:
            Redirect to login page if successful
        """
        if 'confirmdelete' in request.POST:
            self.delete(request.user)
            messages.success(request, _('Successfully deleted account'))
            return redirect('account-login')
        messages.error(request, _('Failed to delete account'))
        return redirect('user-index')

    def delete(self, account: User) -> bool:
        """Handle actual deletion

        Log out user before deleting account with everything attached.

        Args:
            account: The user to delete

        Return:
            True if successful, otherwise False
        """
        if account.delete() != 0:
            django_logout(account)
            return True
        return False
