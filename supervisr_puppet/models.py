"""
Supervisr Puppet Models
"""
import hashlib
import json
import tarfile

from django.db import models


class PuppetUser(models.Model):
    """
    Store Information about a Puppet User
    """
    username = models.TextField()
    display_name = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    @property
    def release_count(self):
        """
        Return Count of releases from this user
        """
        modules = PuppetModule.objects.filter(owner=self)
        releases = PuppetModuleRelease.objects.filter(puppetmodule_set__in=[modules])
        return releases.count()

    @property
    def module_count(self):
        """
        Return Count of modules from this user
        """
        return PuppetModule.objects.filter(owner=self).count()

    def __str__(self):
        return "PuppetUser %s" % (self.username)

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
                    self.metadata = tar.extractfile(file).read()
                    print("Added 'metadata' from targz")

                    try:
                        json.loads(self.metadata.decode("utf-8"))
                    except ValueError:
                        raise
                elif file.lower().endswith('readme.md'):
                    self.readme = tar.extractfile(file).read()
                    print("Added 'readme' from targz")
                elif file.lower().endswith('changelog.md'):
                    self.changelog = tar.extractfile(file).read()
                    print("Added 'changelog' from targz")
                elif file.lower().endswith('license.md'):
                    self.license = tar.extractfile(file).read()
                    print("Added 'license' from targz")
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
    owner = models.ForeignKey(PuppetUser)
    supported = models.BooleanField(default=False)

    def __str__(self):
        return "PuppetModule '%s' by '%s'" % (self.name, self.owner.username)
