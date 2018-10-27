"""supervisr cli cherrypy utils"""
import cherrypy


def run_wsgi(application, log=True, production=False, static_dir=None, config_namespace='default'):
    """Run wsgi application with cherrypy"""
    from supervisr.core.wsgi import WSGILogger
    from django.conf import settings
    # Get default config from django settings
    cherrypy.config.update(settings.CHERRYPY_SERVER.get(config_namespace))
    if production:
        cherrypy.config.update({
            'global': {
                'engine.autoreload.on': False,
                'environment': 'production'
            }
        })
    if static_dir:
        # Mount NullObject to serve static files
        cherrypy.tree.mount(None, static_dir, config={
            '/': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': settings.STATIC_ROOT,
                'tools.expires.on': True,
                'tools.expires.secs': 86400,
                'tools.gzip.on': True,
            }
        })
    if log:
        application = WSGILogger(application)
    cherrypy.tree.graft(application, '/')
    cherrypy.engine.start()
    cherrypy.engine.block()
