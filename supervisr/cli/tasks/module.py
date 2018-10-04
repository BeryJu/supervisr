"""supervisr module tasks"""
from logging import getLogger

from invoke import task
from pip._internal import main  # noqa


@task
# pylint: disable=unused-argument
def install(ctx, url):
    """Install a supervisr module from Git"""
    try:
        import django
    except ImportError:
        print("Django could not be imported")
    django.setup()
    logger = getLogger(__name__)
    module_name = url.split('/')[-1].split('.git')[0]
    main(['install', '-e', 'git+%s#egg=%s' % (url, module_name)])
    logger.success('Successfully installed %s', module_name)
    # TODO: Create .yml file to add module to INSTALLED_APPLICATIONS
