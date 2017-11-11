"""supervisr beacon receiver"""

import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

LOGGER = logging.getLogger(__name__)

@csrf_exempt
def receive(req):
    """receive data and save it"""
    LOGGER.debug(req.POST)
    return HttpResponse('test')
