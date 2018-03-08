"""supervisr module tasks"""
import logging

import pip
from invoke import task

LOGGER = logging.getLogger(__name__)


@task
# pylint: disable=unused-argument
def install(ctx, url):
    """Install a supervisr module from Git"""
    module_name = url.split('/')[-1].split('.git')[0]
    pip.main(['install', '-e', 'git+%s#egg=%s' % (url, module_name)])
