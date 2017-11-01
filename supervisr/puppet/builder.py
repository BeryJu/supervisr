"""
Supervisr Puppet Module Builder
"""
import glob
import gzip
import io
import json
import logging
import os
import tarfile
from tempfile import NamedTemporaryFile

from django import conf
from django.contrib.auth.models import Group, User
from django.core.files import File
from django.template import loader

from supervisr.core.utils import time
from supervisr.puppet.models import PuppetModuleRelease
from supervisr.puppet.utils import ForgeImporter

LOGGER = logging.getLogger(__name__)

# pylint: disable=too-many-instance-attributes
class ReleaseBuilder(object):
    """
    Class to build PuppetModuleRelease's in Memory from files and templates
    """

    module = None
    base_dir = None
    version = None
    output_base = None

    _root_dir = ''
    _spooled_tgz_file = None
    _tgz_file = None
    _release = None

    def __init__(self, module, version=None):
        super(ReleaseBuilder, self).__init__()
        self.module = module
        if self.module.source_path:
            self.base_dir = self.module.source_path
        self.output_base = os.path.join(conf.settings.MEDIA_ROOT, 'puppet', 'modules')
        if conf.settings.TEST:
            # Use test subfolder if we're running as unittest
            self.output_base = os.path.join(self.output_base, 'test')
        os.makedirs(self.output_base, exist_ok=True)
        # If version is None, just use the newest Release's ID + 1
        if version is None:
            releases = PuppetModuleRelease.objects.filter(module=module)
            if releases.exists():
                # Create semantic version from pk with .0.0 appended
                self.version = '1.0.' + str(releases.order_by('-pk').first().pk + 1)
            else:
                self.version = '1.0.0'
        else:
            self.version = version
        self._spooled_tgz_file = io.BytesIO()
        self._tgz_file = tarfile.TarFile(mode='w', fileobj=self._spooled_tgz_file)
        self._root_dir = '%s-%s-%s' % (module.owner.username.lower(), module.name, self.version)
        LOGGER.info('Building %s', self._root_dir)

    def make_context(self, context):
        """
        Add a few variables to the context
        """
        context.update({
            'PUPPET': {
                'module': self.module,
                'version': self.version,
            },
            'settings': conf.settings,
            'puppet_systemgroup': Group.objects.get(name='Puppet Systemusers'),
            'User': User.objects,
            })
        return context

    def to_tarinfo(self, template, ctx, rel_path):
        """
        Convert text to a in-memory file/tarinfo
        """
        # First off render the template
        # Convert it to bytes, create a TarInfo object and add it to the main archive
        byteio = io.BytesIO(self.render_template(template, ctx).encode('utf-8'))
        byteio.seek(0, io.SEEK_END)
        tar_info = tarfile.TarInfo(name=rel_path)
        tar_info.size = byteio.tell()
        byteio.seek(0, io.SEEK_SET)
        self._tgz_file.addfile(tar_info, fileobj=byteio)

    @staticmethod
    def validate_json(body):
        """
        Return True if body is valid JSON, else raise Exception
        """
        try:
            json.loads(body)
            return True
        except ValueError:
            LOGGER.warning(body)
            raise

    @time(statistic_key='puppet.builder.import_deps')
    def import_deps(self):
        """
        Import dependencies for release
        """
        if not self._release:
            return False
        dependencies = json.loads(self._release.metadata)['dependencies']
        importer = ForgeImporter()
        for module in dependencies:
            importer.import_module(module['name'])
        LOGGER.info('Imported dependencies for %s', self._root_dir)

    def render_template(self, path, context=None, check_json=True):
        """
        Render template and return as string
        """
        LOGGER.debug("About to render '%s' for puppet", path)
        if not context:
            context = self.make_context({})
        tmpl = loader.get_template(path)
        rendered = tmpl.render(context)
        # If it's a json file now, check if it's valid
        if path.endswith('.json') and check_json:
            self.validate_json(rendered)
            LOGGER.info('Successfully validated %s', path)
        return rendered

    @time(statistic_key='puppet.builder.build')
    def build(self, context=None, db_add=True, force_rebuild=False):
        """
        Copy non-templates into tar, render templates into tar and import into django
        """
        files = glob.glob('%s/**' % self.base_dir, recursive=True)
        if context is None:
            context = {}
        _context = self.make_context(context)
        for file in files:
            # Render template
            arc_path = file.replace('\\', '/').replace(self.base_dir, self._root_dir + '/')
            if os.path.isdir(file):
                self._tgz_file.add(file, arcname=arc_path, recursive=False)
            else:
                self.to_tarinfo(file, _context, arc_path)
            LOGGER.info('Added %s', arc_path)

        # Flush to file buffer
        self._tgz_file.close()
        # Gzip it so we actually have a tgz
        gzipped = gzip.compress(self._spooled_tgz_file.getbuffer())
        # Write to file and add to db
        module_dir = '%s/%s/%s/' \
                     % (self.output_base, self.module.owner.username, self.module.name)
        prefix = '%s-%s_version_%s_' % (self.module.owner.username, self.module.name, self.version)
        if not os.path.exists(module_dir):
            os.makedirs(module_dir)
        if db_add is True:
            with NamedTemporaryFile(dir=module_dir, suffix='.tgz', prefix=prefix) as temp_file:
                temp_file.write(gzipped)
                temp_file.seek(0, io.SEEK_SET)
                LOGGER.info("Target filename: %s", temp_file.name)
                # Create the module in the db and write it to disk
                self._release = PuppetModuleRelease.objects.create(
                    module=self.module,
                    version=self.version,
                    release=File(temp_file))
        elif force_rebuild is True:
            with open(prefix+'.tgz', mode='w+b') as file:
                file.write(gzipped)
                LOGGER.info("Wrote module to %s", prefix+'.tgz')
