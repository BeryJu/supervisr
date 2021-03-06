"""Supervisr Puppet Models"""
import hashlib
import json
import logging
import tarfile

from django.conf import settings
from django.db import models
from pymysql.err import InternalError

LOGGER = logging.getLogger(__name__)


class PuppetModuleRelease(models.Model):
    """Store Information about a Puppet Module Release"""
    version = models.TextField()
    release = models.FileField(max_length=500)
    downloads = models.IntegerField(default=0)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    module = models.ForeignKey('PuppetModule', on_delete=models.CASCADE)

    readme = models.TextField(blank=True)
    changelog = models.TextField(blank=True)
    license = models.TextField(blank=True)
    metadata = models.TextField(blank=True)

    @property
    def get_size(self):
        """Return size of release (not implemented yet)"""
        return 0

    @property
    def get_md5(self):
        """Return MD5 hash of release"""
        # MD5 specified in puppet forge api spec
        return hashlib.md5(self.release.read()).hexdigest() # nosec

    @property
    def get_downloads(self):
        """Return download count"""
        return self.downloads

    @property
    def get_metaobject(self):
        """Return Metdata as parsed object"""
        return json.loads(self.metadata)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Import metadata, readme, changelog and license on first save"""
        if not self.pk:
            self.readme = ''
            self.changelog = ''
            self.license = ''
            self.metadata = '{}'

            tar = tarfile.open(mode="r:gz", fileobj=self.release)
            for file in tar.getnames():
                if file.lower().endswith('metadata.json'):
                    self.metadata = tar.extractfile(file).read().decode('utf-8')
                    LOGGER.debug("%s: Added 'metadata' from targz", self.module.name)
                    json.loads(self.metadata)
                meta_keys = ['readme', 'changelog', 'license']
                for key in meta_keys:
                    if file.lower().endswith('%s.md' % key):
                        try:
                            setattr(self, key, tar.extractfile(file).read().decode('utf-8'))
                            LOGGER.debug("%s: Added '%s' from targz", self.module.name, key)
                        except InternalError:
                            pass
        super(PuppetModuleRelease, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return "PuppetModuleRelease '%s-%s'" % (self.module.name, self.version)


class PuppetModule(models.Model):
    """Store Information about a Puppet Module"""
    name = models.TextField()
    downloads = models.IntegerField(default=0)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    supported = models.BooleanField(default=False)
    source_path = models.TextField(default='', blank=True)

    def __str__(self):
        return "PuppetModule '%s' by '%s'" % (self.name, self.owner.username)
