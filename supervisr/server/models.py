"""
Superviser Server Models
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _

from supervisr.core.models import CreatedUpdatedModel, Product


class Server(Product):
    """
    Store information about a Server Model
    """
    cpus = models.ForeignKey('ServerCPU', on_delete=models.CASCADE)
    ram = models.IntegerField()
    drives = models.ForeignKey('ServerDrive', on_delete=models.CASCADE)
    nics = models.ManyToManyField('ServerNIC')
    is_virtual = models.BooleanField(default=True)
    is_managed = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ServerCPU(CreatedUpdatedModel):
    """
    Store information about a CPU Model
    """
    cpu_id = models.AutoField(primary_key=True)
    physical_cores = models.IntegerField()
    smt = models.BooleanField()
    frequency = models.IntegerField(default=0)
    make = models.TextField()
    model = models.TextField()

    @property
    def cores(self):
        """
        Return amount of all cores available
        """
        return self.physical_cores * 2 if self.smt else self.physical_cores

    def __str__(self):
        return _("%(make)s %(model)s @ %(frequency)s (%(cores)s Cores)" % {
            'make': self.make,
            'model': self.model,
            'frequency': self.frequency,
            'cores': self.cores
            })

class ServerDrive(CreatedUpdatedModel):
    """
    Store information about a Drive Model
    """
    drive_id = models.AutoField(primary_key=True)
    capacity = models.IntegerField()
    make = models.TextField()
    model = models.TextField()
    rpm = models.IntegerField() # 0 indicates SSD

    @property
    def is_flash(self):
        """
        Returns true if this is an SSD
        """
        return self.rpm == 0

    def __str__(self):
        return _("%(make)s %(model)s %(capacity)sGB (%(rpm)srpm, is_flash: %(is_flash)s)" % {
            'make': self.make,
            'model': self.model,
            'capacity': self.capacity,
            'rpm': self.rpm,
            'is_flash': self.is_flash
            })

class ServerNIC(CreatedUpdatedModel):
    """
    Store information about a Server NIC
    """
    nic_id = models.AutoField(primary_key=True)
    speed = models.IntegerField()
    ips = models.ManyToManyField('IPAddress', blank=True)

    def __str__(self):
        return _("Generic NIC @ %(speed)s Mbits" % {
            'speed': self.speed
            })

class IPAddress(CreatedUpdatedModel):
    """
    Store Information about an IP
    """
    ipaddress_id = models.AutoField(primary_key=True)
    address = models.GenericIPAddressField()
    #server = models.ForeignKey(ServerProduct) this is generated by

    def __str__(self):
        return "IPAddress %s" % self.address
