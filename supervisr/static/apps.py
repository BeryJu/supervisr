"""supervisr Static Apps Config"""
import logging

from django.db.utils import InternalError, OperationalError, ProgrammingError
from django.utils.text import slugify
from supervisr.core.apps import Bootstrapper, SupervisrAppConfig

LOGGER = logging.getLogger(__name__)


class FilePageBootstrapper(Bootstrapper):
    """Bootstrap creation of FilePage instances"""

    def apply(self, invoker):
        from supervisr.static.models import FilePage
        from supervisr.core.models import get_system_user
        for entry in self.rows:
            FilePage.objects.get_or_create(
                path=entry.get('path'),
                title=entry.get('title'),
                language=entry.get('language', 'en'),
                defaults={
                    'author': get_system_user(),
                    'slug': entry.get('slug', slugify(entry.get('title'))),
                    'content': '',
                    'published': True,
                }
            )

class SupervisrStaticConfig(SupervisrAppConfig):
    """supervisr Static app config"""

    name = 'supervisr.static'
    label = 'supervisr_static'
    verbose_name = 'Supervisr Static'
    navbar_enabled = lambda self, request: False
    title_modifier = lambda self, request: 'Static'

    def ready(self):
        super(SupervisrStaticConfig, self).ready()
        try:
            self.update_filepages()
            self.ensure_product_pages()
        except (OperationalError, ProgrammingError, InternalError):
            pass

    def bootstrap(self):
        """Add README and ATTRIBUTIONS FilePage"""
        filepages = FilePageBootstrapper()
        filepages.add(path='README.md', title='Readme')
        filepages.add(path='ATTRIBUTIONS.md', title='Attributions')
        return [filepages, ]

    def update_filepages(self):
        """Update all FilePages from File"""
        from supervisr.static.models import FilePage
        count = 0
        for file_page in FilePage.objects.all():
            if file_page.update_from_file():
                LOGGER.debug("Successfully updated %s with '%s'", file_page.title, file_page.path)
                count += 1
        LOGGER.debug("Successfully updated %d FilePages", count)

    def ensure_product_pages(self):
        """Make sure every Product has a ProductPage"""
        from supervisr.core.models import Product, get_system_user
        from supervisr.static.models import ProductPage
        products = Product.objects.all().exclude(productpage__isnull=False)
        for prod in products:
            ProductPage.objects.create(
                title=prod.name,
                author=get_system_user(),
                slug=prod.slug,
                published=True,
                listed=(not prod.invite_only),
                content=prod.description,
                product=prod)
        LOGGER.debug("Created %d ProductPages", len(products))
