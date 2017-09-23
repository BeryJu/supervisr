"""
Supervisr Web Views
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(req):
    """
    Show empty index page
    """
    return render(req, 'web/index.html')
