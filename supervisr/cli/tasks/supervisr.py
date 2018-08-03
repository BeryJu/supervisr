"""supervisr tasks"""

from invoke import task
from invoke.terminals import WINDOWS


@task
# pylint: disable=unused-argument
def migrate(ctx):
    """Apply migrations"""
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate'])


@task
def run_celery(ctx, debug=False):
    """Run Celery worker"""
    if debug and WINDOWS:
        # Workaround since celery is not supported on windows since version 4
        # https://github.com/celery/celery/issues/4178
        ctx.run("celery -A supervisr.core worker -l info -Ofair -c 1 --pool=solo", pty=True)
    elif debug:
        ctx.run("celery -A supervisr.core worker -l debug -Ofair -c 1", pty=True)
    else:
        ctx.run("celery -A supervisr.core worker -l info -Ofair", pty=True)


@task
def run_celery_beat(ctx):
    """Run Celery beat worker"""
    ctx.run("celery -A supervisr.core beat")


@task
def run_celery_flower(ctx):
    """Run Celery flower"""
    ctx.run(("celery -A supervisr.core flower --address=127.0.0.1 "
             "--url_prefix=/app/mod/web/proxy/supervisr_flower"))


@task
# pylint: disable=unused-argument
def run(ctx, pidfile='', listen=None, port=None):
    """Run CherryPY-based application server"""
    from django.conf import settings
    from supervisr.core.wsgi import application
    from cherrypy.process.plugins import PIDFile
    import cherrypy

    # pylint: disable=too-few-public-methods
    class NullObject(object):
        """empty class to serve static files with cherrypy"""

    cherrypy.config.update({
        'log.screen': False,
        'log.access_file': '',
        'log.error_file': ''
    })
    cherrypy.tree.graft(application, '/')
    # Mount NullObject to serve static files
    cherrypy.tree.mount(NullObject(), '/static', config={
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': settings.STATIC_ROOT,
        }
    })
    cherrypy.server.unsubscribe()
    # pylint: disable=protected-access
    server = cherrypy._cpserver.Server()

    server.thread_pool = 30
    for key, value in settings.CHERRYPY_SERVER.items():
        setattr(server, key, value)
    if listen:
        server.socket_host = listen
    if port:
        server.socket_port = port
    server.subscribe()

    if pidfile != '':
        PIDFile(cherrypy.engine, pidfile).subscribe()

    cherrypy.engine.start()
    cherrypy.engine.block()
