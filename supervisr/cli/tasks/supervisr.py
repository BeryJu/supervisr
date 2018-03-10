"""supervisr tasks"""

from invoke import task


@task()
# pylint: disable=unused-argument
def migrate(ctx):
    """Apply migrations"""
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate'])


@task
# pylint: disable=unused-argument
def run(ctx, pidfile='', listen='0.0.0.0', port=8000):
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

    server.socket_host = listen
    server.socket_port = port
    server.thread_pool = 30
    for key, value in settings.CHERRYPY_SERVER.items():
        setattr(server, key, value)
    server.subscribe()

    if pidfile != '':
        PIDFile(cherrypy.engine, pidfile).subscribe()

    cherrypy.engine.start()
    cherrypy.engine.block()
