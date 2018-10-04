"""supervisr build tasks"""
from logging import getLogger

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
def debian(ctx, signed=False, cleanup=True):
    """Build debian package"""
    ctx.run("cp -R build/debian .")
    if signed:
        ctx.run('dpkg-buildpackage')
    else:
        ctx.run('dpkg-buildpackage -us -uc')
    if cleanup:
        ctx.run('rm -rf debian/')

@task
def docker(ctx):
    """Build debian package"""
    ctx.run('docker-compose --file build/docker/docker-compose.yml build supervisr')
    ctx.run(('docker-compose --file build/docker/docker-compose.debug.yml run supervisr '
             'build/docker/start_wrapper.sh "inv ci.unittest"'))

@task
def pypi(ctx, test=True):
    """Build dist and egg packages and upload them."""
    ctx.run('rm -f dist/*')
    ctx.run('python setup.py sdist bdist_wheel')
    if test:
        ctx.run('twine upload --repository-url https://test.pypi.org/legacy/ dist/*')
    else:
        ctx.run('twine upload dist/*')
