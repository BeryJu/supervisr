"""
Supervisr Invoke Tasks
"""
import logging

from invoke import task

try:
    import django
    from django.db.utils import IntegrityError
except ImportError:
    print("Django could not be imported")

LOGGER = logging.getLogger(__name__)

@task()
# pylint: disable=unused-argument
def migrate(ctx):
    """
    Apply migrations
    """
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate'])

@task()
# pylint: disable=unused-argument
def list_users(ctx):
    """
    Show a list of all users
    """
    django.setup()
    from django.contrib.auth.models import User
    users = User.objects.all().order_by('pk')
    LOGGER.info("Listing users...")
    for user in users:
        LOGGER.info("id=%d username=%s", user.pk, user.username)

@task
# pylint: disable=unused-argument
def make_superuser(ctx, uid):
    """
    Make User with uid superuser.
    This should be run after `./manage.py createsuperuser` or
    after you sign up on the webinterface as first user
    """
    django.setup()
    from supervisr.core.models import UserProfile
    from django.contrib.auth.models import User
    user = User.objects.filter(pk=uid).first()
    LOGGER.info("About to make '%s' superuser...", user.username)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    try:
        # UserProfile might already exist
        # if user signed up with webinterface
        UserProfile.objects.create(user=user)
    except IntegrityError:
        pass
    LOGGER.info("Done!")

@task
# pylint: disable=unused-argument
def run(ctx, pidfile=''):
    """
    Run CherryPY-based application server
    """
    from django.conf import settings
    from supervisr.core.wsgi import application
    from cherrypy.process.plugins import PIDFile
    import cherrypy

    # pylint: disable=too-few-public-methods
    class NullObject(object):
        """
        empty class to serve static files with cherrypy
        """

    cherrypy.config.update({'log.screen': False,
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

    server.socket_host = "0.0.0.0"
    server.socket_port = 8000
    server.thread_pool = 30
    for key, value in settings.CHERRYPY_SERVER.items():
        setattr(server, key, value)
    server.subscribe()

    if pidfile != '':
        PIDFile(cherrypy.engine, pidfile).subscribe()

    cherrypy.engine.start()
    cherrypy.engine.block()
