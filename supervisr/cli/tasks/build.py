"""supervisr build tasks"""
import os
from logging import getLogger

import requests
from invoke import task

LOGGER = getLogger(__name__)


@task
def appliance(ctx):
    """Build supervisr appliance using packer"""
    modules = ['puppetlabs-mysql', 'puppetlabs-apt', 'arioch-redis']
    with ctx.cd('build/packer'):
        for module in modules:
            ctx.run('/opt/puppetlabs/bin/puppet module install -i puppet/ %s' % module)
        LOGGER.success('Successfully prepared puppet modules.')
        ctx.run('packer build packer.json')

@task
def debian(ctx, signed=False, cleanup=True, upload=False):
    """Build debian package"""
    ctx.run('cp CHANGELOG build/debian/changelog')
    ctx.run("cp -R build/debian .")
    if signed:
        ctx.run('dpkg-buildpackage')
    else:
        ctx.run('dpkg-buildpackage -us -uc')
    if cleanup:
        ctx.run('rm -rf debian/')
    if upload:
        from supervisr import __version__
        nexus_url = os.environ.get('NEXUS_URL')
        nexus_user = os.environ.get('NEXUS_USER')
        nexus_pass = os.environ.get('NEXUS_PASS')
        requests.post('https://%s/repository/apt/' % nexus_url,
                      data=open('../supervisr_%s_amd64.deb' % __version__, mode='rb'),
                      auth=(nexus_user, nexus_pass))

@task
def docker(ctx):
    """Build debian package"""
    ctx.run('docker-compose --file build/docker/docker-compose.yml build supervisr')
    ctx.run(('docker-compose --file build/docker/docker-compose.debug.yml run supervisr '
             'build/docker/start_wrapper.sh "inv env.unittest"'))

@task
def pypi(ctx, test=True):
    """Build dist and egg packages and upload them."""
    ctx.run('rm -f dist/*')
    ctx.run('python setup.py sdist bdist_wheel')
    if test:
        ctx.run('twine upload --repository-url https://test.pypi.org/legacy/ dist/*')
    else:
        ctx.run('twine upload dist/*')

@task
# pylint: disable=invalid-name
def ui(context):
    """Build Angular App with webpack"""
    from django.conf import settings
    with context.cd(settings.BASE_DIR + '/ui'):
        context.run('npm run-script build')
