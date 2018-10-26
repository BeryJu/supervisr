"""Supervisr Core check_template_syntax ManagementCommand"""
from glob import glob
from logging import getLogger

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import Context, Template, TemplateSyntaxError
from django.template.loaders.app_directories import get_app_template_dirs

LOGGER = getLogger(__name__)


class Command(BaseCommand):
    """Check syntax of all project templates"""

    help = 'Check syntax of all project templates'

    def handle(self, *args, **options):
        return_code = 0
        for template_dir in get_app_template_dirs('templates'):
            if template_dir.startswith(settings.BASE_DIR):
                for template_file in glob('%s/**/*html' % template_dir, recursive=True):
                    short_path = template_file.replace(settings.BASE_DIR, '')
                    try:
                        tmpl = Template(template_file)
                        tmpl.render(Context())
                        LOGGER.info('%s passed successfully!', short_path)
                    except TemplateSyntaxError as exc:
                        LOGGER.error('%s errored: %s', short_path, exc)
                        return_code = 1
        return return_code
