"""
Supervisr Web Views
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    """Show empty index page"""
    return render(request, 'web/index.html')
