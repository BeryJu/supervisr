"""
Supervisr Puppet Models
"""
import hashlib
import json
import logging
import tarfile

from django.contrib.auth.models import User
from django.db import models

LOGGER = logging.getLogger(__name__)

class PuppetModuleRelease(models.Model):
    """
    Store Information about a Puppet Module Release
    """
    version = models.TextField()
    release = models.FileField()
    downloads = models.IntegerField(default=0)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    module = models.ForeignKey('PuppetModule')

    readme = models.TextField(blank=True)
    changelog = models.TextField(blank=True)
    license = models.TextField(blank=True)
    metadata = models.TextField(blank=True)

    @property
    def get_size(self):
        """
        Return size of release (not implemented yet)
        """
        return 0

    @property
    def get_md5(self):
        """
        Return MD5 hash of release
        """
        return hashlib.md5(self.release.read()).hexdigest()

    @property
    def get_downloads(self):
        """
        Return download count
        """
        return self.downloads

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Import metadata, readme, changelog and license on first save
        """
        if not self.pk:
            self.readme = ''
            self.changelog = ''
            self.license = ''
            self.metadata = '{}'

            tar = tarfile.open(mode="r:gz", fileobj=self.release)
            for file in tar.getnames():
                if file.lower().endswith('metadata.json'):
                    self.metadata = tar.extractfile(file).read().decode('utf-8')
                    LOGGER.info("%s: Added 'metadata' from targz", self.module.name)
                    try:
                        json.loads(self.metadata)
                    except ValueError:
                        raise
                elif file.lower().endswith('readme.md'):
                    self.readme = tar.extractfile(file).read().decode('utf-8')
                    LOGGER.info("%s: Added 'readme' from targz", self.module.name)
                elif file.lower().endswith('changelog.md'):
                    self.changelog = tar.extractfile(file).read().decode('utf-8')
                    LOGGER.info("%s: Added 'changelog' from targz", self.module.name)
                elif file.lower().endswith('license.md'):
                    self.license = tar.extractfile(file).read().decode('utf-8')
                    LOGGER.info("%s: Added 'license' from targz", self.module.name)
        super(PuppetModuleRelease, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return "PuppetModuleRelease '%s-%s'" % (self.module.name, self.version)

class PuppetModule(models.Model):
    """
    Store Information about a Puppet Module
    """
    name = models.TextField()
    downloads = models.IntegerField(default=0)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User)
    supported = models.BooleanField(default=False)

    def __str__(self):
        return "PuppetModule '%s' by '%s'" % (self.name, self.owner.username)
