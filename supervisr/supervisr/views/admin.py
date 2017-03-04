"""
Supervisr Core Admin Views
"""

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render


@login_required
@user_passes_test(lambda u: u.is_superuser)
def index(req):
    """
    Admin index
    """
    # Subtract the system user
    user_count = User.objects.all().count() -1
    return render(req, '_admin/index.html', {
        'user_count': user_count,
        })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def settings(req):
    """
    Admin settings
    """
    return render(req, '_admin/index.html')
