"""
Supervisr Puppet Module Builder
"""
import gzip
import io
import json
import logging
import os
import tarfile
import sys
from tempfile import TemporaryFile

from django.core.files import File
from django.template import loader

from supervisr.utils import time

from .models import PuppetModuleRelease
from .utils import ForgeImporter

LOGGER = logging.getLogger(__name__)


class ReleaseBuilder(object):
    """
    Class to build PuppetModuleRelease's in Memory from files and templates
    """

    module = None
    extension = '.djt'
    base_dir = None
    version = None

    _root_dir = ''
    _spooled_tgz_file = None
    _tgz_file = None
    _release = None

    def __init__(self, module, version=None):
        super(ReleaseBuilder, self).__init__()
        self.module = module
        # If version is None, just use the newest Release's ID + 1
        if version is None:
            releases = PuppetModuleRelease.objects.filter(module=module)
            if releases.exists():
                # Create semantic version from pk with .0.0 appended
                self.version = str(releases.order_by('-pk').first().pk + 1)+'.0.0'
            else:
                self.version = '1'
        else:
            self.version = version
        self._spooled_tgz_file = io.BytesIO()
        self._tgz_file = tarfile.TarFile(mode='w', fileobj=self._spooled_tgz_file)
        self._root_dir = '%s-%s-%s' % (module.owner.first_name.lower(), module.name, self.version)
        LOGGER.info('Building %s', self._root_dir)

    def make_context(self, context):
        """
        Add a few variables to the context
        """
        context.update({
            'PUPPET': {
                'module': self.module,
                'version': self.version,
            }})
        return context

    def to_tarinfo(self, template, ctx, rel_path):
        """
        Convert text to a in-memory file/tarinfo
        """
        # First off render the template
        tmpl = loader.get_template(template)
        rendered = tmpl.render(ctx)
        # Create the new path without the .djt
        new_path = rel_path.replace(self.extension, '')
        # If it's a json file now, check if it's valid
        if new_path.endswith('.json'):
            self.validate_json(rendered)
            LOGGER.info('Successfully validated %s', new_path)
        # Convert it to bytes, create a TarInfo object and add it to the main archive
        byteio = io.BytesIO(rendered.encode('utf-8'))
        byteio.seek(0, io.SEEK_END)
        tar_info = tarfile.TarInfo(name=new_path)
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
            LOGGER.error(body)
            raise

    @time
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

    def _glob_helper(list_dir):
        if sys.version_info >= (3,5):
            # Python 3.5 has a glob function with recursion
            import glob
            # pylint: disable=unexpected-keyword-arg
            return glob.glob('%s/**' % list_dir, recursive=True)
        else:
            root, dirnames, filenames = os.walk(list_dir)
            return filenames

    @time
    def build(self, context=None):
        """
        Copy non-templates into tar, render templates into tar and import into django
        """
        files = self._glob_helper('%s/**' % self.base_dir)
        if context is None:
            context = {}
        _context = self.make_context(context)
        for file in files:
            # Render template if matches extension
            arc_path = file.replace(self.base_dir, self._root_dir).replace('\\', '/')
            if arc_path.endswith(self.extension):
                self.to_tarinfo(file, _context, arc_path)
            else:
                self._tgz_file.add(file, arcname=arc_path, recursive=False)
            LOGGER.info('Added %s', arc_path)

        # Flush to file buffer
        self._tgz_file.close()
        # Gzip it so we actually have a tgz
        gzipped = gzip.compress(self._spooled_tgz_file.getbuffer())
        # Write to file and add to db
        module_dir = 'supervisr_puppet/modules/%s/%s' \
                     % (self.module.owner.first_name, self.module.name)
        prefix = 'version_%s_' % self.version
        if not os.path.exists(module_dir):
            os.makedirs(module_dir)

        with TemporaryFile(dir=module_dir, suffix='.tgz', prefix=prefix) as temp_file:
            temp_file.write(gzipped)
            temp_file.seek(0, io.SEEK_SET)
            # Create the module in the db and write it to disk
            self._release = PuppetModuleRelease.objects.create(
                module=self.module,
                version=self.version,
                release=File(temp_file))
