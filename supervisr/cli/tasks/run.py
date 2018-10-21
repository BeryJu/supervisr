"""supervisr tasks"""
import os

import cherrypy
from invoke import task
from invoke.terminals import WINDOWS


@task
# pylint: disable=unused-argument
def migrate(ctx):
    """Apply migrations"""
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate_all'])


@task
def worker(ctx, debug=False):
    """Run Celery worker"""
    if debug and WINDOWS:
        # Workaround since celery is not supported on windows since version 4
        # https://github.com/celery/celery/issues/4178
        ctx.run("celery -A supervisr.core worker -l info -Ofair -c 1 --pool=solo", pty=True)
    elif debug:
        ctx.run("celery -A supervisr.core worker -l debug -Ofair --autoscale=10,3 -E", pty=True)
    else:
        os.environ.setdefault('SUPERVISR_COMPONENT', 'task-runner')
        ctx.run("celery -A supervisr.core worker -l info -Ofair --autoscale=10,3", pty=True)


@task
def worker_scheduler(ctx):
    """Run Celery beat worker"""
    os.environ.setdefault('SUPERVISR_COMPONENT', 'task-scheduler')
    ctx.run("celery -A supervisr.core beat")


@task
def worker_monitor(ctx):
    """Run Celery flower"""
    os.environ.setdefault('SUPERVISR_COMPONENT', 'task-monitor')
    ctx.run(("celery -A supervisr.core flower --address=127.0.0.1 --logging=none "
             "--url_prefix=/app/mod/web/proxy/supervisr_flower"))


@task
# pylint: disable=unused-argument
def web(ctx, pidfile='', production=False):
    """Run CherryPY-based application server"""
    from django.conf import settings
    from supervisr.core.wsgi import application, WSGILogger
    os.environ.setdefault('SUPERVISR_COMPONENT', 'web')
    # Get default config from django settings
    cherrypy.config.update(settings.CHERRYPY_SERVER)
    if production:
        cherrypy.config.update({
            'global': {
                'engine.autoreload.on': False,
                'environment': 'production'
            }
        })
    # Mount NullObject to serve static files
    cherrypy.tree.mount(None, '/static', config={
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': settings.STATIC_ROOT,
            'tools.expires.on': True,
            'tools.expires.secs': 86400,
            'tools.gzip.on': True,
        }
    })
    cherrypy.tree.graft(WSGILogger(application), '/')
    if pidfile != '':
        cherrypy.process.plugins.PIDFile(cherrypy.engine, pidfile).subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()

@task
# pylint: disable=invalid-name
def ui(context):
    """Run Angular CLI debug server"""
    from django.conf import settings
    with context.cd(settings.BASE_DIR + '/ui'):
        context.run('npm start')
