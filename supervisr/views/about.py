"""
Supervisr Core About Views
"""

from django.conf import settings
from django.shortcuts import render


def changelog(req):
    """
    Show Changelog, which is read from ../../CHANGELOG.md
    """
    return render(req, 'about/changelog.html', {
        'changelog': settings.CHANGELOG
        })
