"""
Supervisr Mail Common Views
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(req):
    """
    Mail index
    """
    return render(req, 'mail/index.html')
