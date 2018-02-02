"""Supervisr Core Middleware to detect Deploy Page Mode"""

import os

from django.conf import settings
from django.shortcuts import render

DEPLOY_PAGE_PATH = os.path.join(settings.BASE_DIR, 'core/templates/core/deploy.html')

def deploy_page(get_response):
    """Middleware to detect Deploy Page Mode"""

    def middleware(request):
        """Middleware to detect Deploy Page Mode"""

        if os.path.exists(DEPLOY_PAGE_PATH):
            return render(request, 'core/deploy.html')
        response = get_response(request)
        return response
    return middleware
