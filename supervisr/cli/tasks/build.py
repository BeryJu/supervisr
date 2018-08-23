"""supervisr build tasks"""
from invoke import task

from supervisr.core.logger import SupervisrLogger

LOGGER = SupervisrLogger(__name__)


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
