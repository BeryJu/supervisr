from __future__ import unicode_literals
from django.db import models
from django.db.utils import OperationalError
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
import uuid
import json
import time

NOTIFICATION_IMPORTANCE = (
    (40, _('Urgent')),
    (30, _('Important')),
    (20, _('Medium')),
    (10, _('Notice')),
    (0, _('Information'))
)
NOTIFICATION_IMPORTANCE_URGENT = 40
NOTIFICATION_IMPORTANCE_IMPORTANT = 30
NOTIFICATION_IMPORTANCE_MEDIUM = 20
NOTIFICATION_IMPORTANCE_NOTICE = 10
NOTIFICATION_IMPORTANCE_INFORMATION = 0

ACCOUNT_CONFIRMATION_KIND = (
    (0, _('Sign up')),
    (1, _('Password Reset')),
)
ACCOUNT_CONFIRMATION_KIND_SIGN_UP = 0
ACCOUNT_CONFIRMATION_KIND_PASSWORD_RESET = 1

def expiry_date():
    return time.time() + 172800 # 2 days

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    locale = models.CharField(max_length=5, default='en-US')

class Setting(models.Model):
    key = models.TextField(primary_key=True)
    value = models.TextField()
    value_json_cached = None

    @property
    def value_bool(self):
        return self.value.lower() == 'true'

    def set_bool(self, value):
        self.value = str(value)

    def __str__(self):
        return "Setting %s" % self.key

    @staticmethod
    def get(key, default=''):
        try:
            setting, created = Setting.objects.get_or_create(
                key=key,
                defaults={'value': default})
            return setting
        except OperationalError as e:
            # Migrations have not been applied yet, just ignore it
            return Setting(key='temp', value=default)

class AccountConfirmation(models.Model):
    account_confirmation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)
    expires = models.BigIntegerField(default=expiry_date, editable=False)
    confirmed = models.BooleanField(default=False)
    kind = models.IntegerField(choices=ACCOUNT_CONFIRMATION_KIND, default=0)

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    source_user = models.ForeignKey(User, related_name='outgoing_notifications')
    destination_user = models.ForeignKey(User, related_name='incoming_notifications')
    destination_link = models.TextField()
    importance = models.IntegerField(choices=NOTIFICATION_IMPORTANCE, default=0)
    read = models.BooleanField(default=False)

    def __str__(self):
        return _("Notification %(source_user)s %(destination_user)s" % {
            'user': self.user,
            'product': self.product,
            })

class UserProductRelationship(models.Model):
    user_product_relationship_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    product = models.ForeignKey('Product')
    instance_name = models.TextField(blank=True, null=True)
    expiry_delta = models.BigIntegerField(default=0)
    discount_percent = models.IntegerField(default=0)

    @property
    def name(self):
        if self.instance_name:
            return self.instance_name
        return self.product.name

    def __str__(self):
        return _("UserProductRelationship %(product)s %(user)s" % {
            'user': self.user,
            'product': self.product,
            })

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.TextField()
    slug = models.TextField()
    description = models.TextField()
    price = models.DecimalField(decimal_places=3, max_digits=65)
    invite_only = models.BooleanField(default=False)
    users = models.ManyToManyField(User, through='UserProductRelationship')
    managed = models.BooleanField(default=True)
    management_url = models.URLField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.name

class ServerProduct(models.Model):
    server_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product)
    name = models.TextField()
    cpus = models.ForeignKey('ServerCPU')
    ram = models.IntegerField()
    drives = models.ForeignKey('ServerDrive')
    nics = models.ManyToManyField('ServerNIC')
    is_virtual = models.BooleanField(default=True)
    is_managed = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ServerCPU(models.Model):
    cpu_id = models.AutoField(primary_key=True)
    physical_cores = models.IntegerField()
    smt = models.BooleanField()
    frequency = models.IntegerField(default=0)
    make = models.TextField()
    model = models.TextField()

    @property
    def cores(self):
        return self.physical_cores * 2 if self.smt else self.physical_cores

    def __str__(self):
        return _("%(make)s %(model)s @ %(frequency)s (%(cores)s Cores)" % {
            'make': self.make,
            'model': self.model,
            'frequency': self.frequency,
            'cores': self.cores
            })

class ServerDrive(models.Model):
    drive_id = models.AutoField(primary_key=True)
    capacity = models.IntegerField()
    make = models.TextField()
    model = models.TextField()
    rpm = models.IntegerField() # 0 indicates SSD

    @property
    def is_flash(self):
        return self.rpm == 0

    def __str__(self):
        return _("%(make)s %(model)s %(capacity)sGB (%(rpm)srpm, is_flash: %(is_flash)s)" % {
            'make': self.make,
            'model': self.model,
            'capacity': self.capacity,
            'rpm': self.rpm,
            'is_flash': self.is_flash
            })

class ServerNIC(models.Model):
    nic_id = models.AutoField(primary_key=True)
    speed = models.IntegerField()
    ips = models.ManyToManyField('IPAddress', blank=True)

    def __str__(self):
        return _("Generic NIC @ %(speed)s Mbits" % {
            'speed': self.speed
            })

class IPAddress(models.Model):
    ipaddress_id = models.AutoField(primary_key=True)
    address = models.GenericIPAddressField()
    #server = models.ForeignKey(ServerProduct) this is generated by

class HostedApplicationProduct(models.Model):
    hosted_application_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product)
    name = models.TextField()
    version = models.TextField()
    developer = models.TextField()
    developer_site = models.URLField(max_length=1000)

    def __str__(self):
        return self.name
