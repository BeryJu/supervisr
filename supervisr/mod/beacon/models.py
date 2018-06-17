"""Supervisr Beacon Models"""

from django.db import models
from django.utils.translation import ugettext as _
from supervisr.core.models import CreatedUpdatedModel


class Pulse(CreatedUpdatedModel):
    """Model to store data received by and install"""

    pulse_id = models.AutoField(primary_key=True)
    install_id = models.UUIDField(verbose_name=_("Installation's unique ID"))
    time = models.DateTimeField(auto_now_add=True)
    python_version = models.CharField(max_length=100)
    os_uname = models.CharField(max_length=255)
    user_count = models.BigIntegerField(verbose_name=_('Approximate user count'))
    domain_count = models.BigIntegerField(verbose_name=_('Approximate domain count'))
    modules = models.ManyToManyField('PulseModule')

    def __str__(self):
        return "Pulse %s from %s" % (self.install_id, self.time)


class PulseModule(models.Model):
    """Model to store information about an installed module"""

    pulse_module_id = models.AutoField(primary_key=True)
    module_root = models.TextField()
    name = models.TextField()
    author = models.TextField()
    author_email = models.EmailField()

    def __str__(self):
        return "PulseModule %s by %s <%s>" % (self.name, self.author, self.author_email)


class PulseModuleVersion(models.Model):
    """Store different versions of modules"""

    pulse_module_version_id = models.AutoField(primary_key=True)
    pulse_module = models.ForeignKey('PulseModule', on_delete=models.CASCADE)
    version = models.TextField()

    def __str__(self):
        return "PulseModuleVersion %s@%s" % (self.pulse_module.name, self.version)
