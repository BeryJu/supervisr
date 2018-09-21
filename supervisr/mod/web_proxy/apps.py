"""Supervisr module web_proxy app config"""

from supervisr.core.apps import Bootstrapper, SupervisrAppConfig


class WebApplicationBootstrapper(Bootstrapper):
    """Bootstrapper to create WebApplications"""

    def apply(self, invoker):
        from supervisr.mod.web_proxy.models import WebApplication
        for row in self.rows:
            access_slug = row.get('access_slug')
            WebApplication.objects.get_or_create(access_slug=access_slug, defaults=row)


class SupervisrModWebProxyConfig(SupervisrAppConfig):
    """Supervisr module web_proxy app config"""

    name = 'supervisr.mod.web_proxy'
    label = 'supervisr_mod_web_proxy'
    title_modifier = lambda self, request: 'Web Proxy'

    def bootstrap(self):
        """Add default flower Reverse-Proxy"""
        wap_bootstrapper = WebApplicationBootstrapper()
        wap_bootstrapper.add(name='supervisr Flower',
                             access_slug='supervisr_flower',
                             upstream='http://localhost:5555')
        return wap_bootstrapper,
