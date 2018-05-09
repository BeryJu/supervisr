"""supervisr module tasks"""
import logging

from invoke import task
from pip._internal import main  # noqa

LOGGER = logging.getLogger(__name__)


@task
# pylint: disable=unused-argument
def install(ctx, url):
    """Install a supervisr module from Git"""
    module_name = url.split('/')[-1].split('.git')[0]
    main(['install', '-e', 'git+%s#egg=%s' % (url, module_name)])
