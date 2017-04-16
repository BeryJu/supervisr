"""
Supervisr Puppet Module Builder
"""
import gzip
import io
import json
import logging
import tarfile
from glob import glob
from tempfile import TemporaryFile

from django.core.files import File
from django.template import loader

from supervisr.utils import time

from .models import PuppetModuleRelease

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

    def __init__(self, module, version=None):
        super(ReleaseBuilder, self).__init__()
        self.module = module
        # If version is None, just use the newest Release's ID + 1
        if version is None:
            releases = PuppetModuleRelease.objects.filter(module=module)
            if releases.exists():
                self.version = str(releases.order_by('-pk').first().pk + 1)
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
    def build(self, context=None):
        """
        Copy non-templates into tar, render templates into tar and import into django
        """
        # pylint: disable=unexpected-keyword-arg
        files = glob('%s/**' % self.base_dir, recursive=True)
        if context is None:
            context = {}
        _context = self.make_context(context)
        for file in files:
            # Render template if matches extension
            arc_path = file.replace(self.base_dir, self._root_dir)
            if arc_path.endswith(self.extension):
                self.to_tarinfo(file, _context, arc_path)
            else:
                self._tgz_file.add(file, arcname=arc_path, recursive=False)
            LOGGER.info('Added %s', arc_path)

        # Flush to file buffer
        self._tgz_file.close()
        # Gzip it so we actually have a tgz
        gzipped = gzip.compress(self._spooled_tgz_file.getbuffer())
        # Write to temp file
        with TemporaryFile(dir='.') as temp_file:
            temp_file.write(gzipped)
            temp_file.seek(0, io.SEEK_SET)
            # Create the module in the db and write it to disk
            PuppetModuleRelease.objects.create(
                module=self.module,
                version=self.version,
                release=File(temp_file))
