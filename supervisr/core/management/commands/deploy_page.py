"""Supervisr Core deploy page ManagementCommand"""

import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand

LOGGER = logging.getLogger(__name__)
DEPLOY_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta content="width=device-width, initial-scale=1, maximum-scale=1" name="viewport">
  <meta name="refresh" content="60">
  <meta name="retry-after" content="100">
  <meta name="robots" content="noindex, nofollow, noarchive, nostore">
  <meta name="cache-control" content="no-cache, no-store">
  <meta name="pragma" content="no-cache">
  <title>Deploy in progress</title>
  <style>
    body {
      color: #666;
      text-align: center;
      font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
      margin: auto;
      font-size: 14px;
    }

    h1 {
      font-size: 56px;
      line-height: 100px;
      font-weight: 400;
      color: #737373;
    }

    h3 {
      color: #737373;
      font-size: 20px;
      font-weight: 400;
      line-height: 28px;
    }

    hr {
      max-width: 800px;
      margin: 18px auto;
      border: 0;
      border-top: 1px solid #EEE;
      border-bottom: 1px solid white;
    }

    svg {
      max-height: 20vw;
    }

    svg path {
      fill: #0094D2;
    }

    .container {
      margin: auto 20px;
    }
  </style>
</head>

<body>
  <h1>
    <svg version="1.0" xmlns="http://www.w3.org/2000/svg" width="512.000000pt" height="512.000000pt" viewBox="0 0 512.000000 512.000000" preserveAspectRatio="xMidYMid meet"><g transform="translate(0.000000,512.000000) scale(0.100000,-0.100000)" stroke="none"><path d="M1454 4995 c-27 -41 -106 -354 -101 -397 3 -25 28 -70 73 -135 181 -261 398 -573 495 -713 l107 -156 -124 -1309 c-68 -721 -124 -1330 -124 -1355 0 -57 9 -69 150 -221 63 -68 151 -162 195 -209 44 -47 145 -156 225 -243 l145 -157 65 0 65 1 390 374 c215 206 396 388 404 404 12 25 11 51 -8 197 -12 93 -71 563 -132 1044 -60 481 -127 1010 -148 1175 l-38 300 107 155 c93 135 260 375 494 713 45 65 70 110 73 135 5 43 -74 356 -101 397 -15 22 -23 25 -80 25 -66 0 -93 -12 -274 -119 -29 -17 -55 -31 -57 -31 -3 0 -104 -56 -225 -125 -121 -69 -221 -125 -223 -125 -2 0 -54 -29 -117 -65 -63 -36 -121 -65 -130 -65 -9 0 -67 29 -130 65 -63 36 -115 65 -117 65 -2 0 -102 56 -223 125 -121 69 -222 125 -225 125 -2 0 -28 14 -57 31 -181 107 -208 119 -274 119 -57 0 -65 -3 -80 -25z m1226 -1046 c63 -110 116 -206 118 -214 3 -13 -31 -15 -238 -15 -207 0 -241 2 -238 15 4 18 231 414 238 414 3 0 57 -90 120 -200z"/></g></svg><br>
    Deploy in progress
  </h1>
  <div class="container">
    <h3>Please try again in a few minutes.</h3>
    <hr />
    <p>Please contact your supervisr administrator if this problem persists.</p>
  </div>
</body>
</html>
"""  # noqa


class Command(BaseCommand):
    """Turns deploy page on or off via manage.py"""

    help = 'Turns deploy page on or off'

    def add_arguments(self, parser):
        parser.add_argument('state', type=str)

    def handle(self, *args, **options):
        value = options['state'].lower() in ('on', 'true', 'yes', 'up')
        deploy_page_path = os.path.join(settings.BASE_DIR, 'core/templates/core/deploy.html')
        if value:
            with open(deploy_page_path, 'w') as _file:
                _file.write(DEPLOY_PAGE_HTML)
            LOGGER.info("Enabled Deploy Page")
        else:
            try:
                os.unlink(deploy_page_path)
                LOGGER.info("Disabled Deploy Page")
            except FileNotFoundError:
                LOGGER.info("Deploy Page was already disabled.")
            except IOError:
                LOGGER.warning("Failed to disable Deploy Page")
                raise
