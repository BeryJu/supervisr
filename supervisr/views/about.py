"""
Supervisr Core About Views
"""

from django.conf import settings
from django.shortcuts import render


def changelog(req):
    """
    Show Changelog, which is read from CHANGELOG.md
    """
    try:
        file = open('CHANGELOG.md', 'r')
        text = file.read()
        file.close()
    except (OSError, IOError):
        raise
    return render(req, 'about/changelog.html', {
        'changelog': text
        })

def attributions(req):
    """
    Show Attributions, which is read from ATTRIBUTIONS.md
    """
    try:
        file = open('ATTRIBUTIONS.md', 'r')
        text = file.read()
        file.close()
    except (OSError, IOError):
        raise
    return render(req, 'about/attributions.html', {
        'attributions': text
        })

