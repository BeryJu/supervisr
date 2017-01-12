from __future__ import unicode_literals
from django.db import models
from django.db.models import Max
from django.db.utils import OperationalError
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
import uuid
import json
import time
import random
import base64

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

USER_PROFILE_ID_START = 5000

def expiry_date():
    return time.time() + 172800 # 2 days

def get_username():
    # Generate a normal UUID, convert it to base64 and take the 10 first chars
    u = uuid.uuid4()
    # UUID in base64 is 25 chars, we want 10 char length
    offset = random.randint(0, 15)
    # Python3 changed the way we need to encode
    res = base64.b64encode(u.bytes, altchars=b'_-')
    return res[offset:offset+10]

def get_userid():
    # Custom default to set the unix_userid since we can't have an
    # AutoField as non-primary-key. Also so we can set a custom start,
    # which is USER_PROFILE_ID_START
    try:
        highest = UserProfile.objects.all.aggregate(Max('unix_userid'))
        return highest + 1
    except Exception as e:
        return USER_PROFILE_ID_START

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    unix_username = models.CharField(max_length=10, default=get_username, editable=False)
    unix_userid = models.IntegerField(default=get_userid)
    locale = models.CharField(max_length=5, default='en-US')

    def __str__(self):
        return "UserProfile %s" % self.user.email

class Setting(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
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
    account_confirmation_id = models.UUIDField(primary_key=True, \
        default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)
    expires = models.BigIntegerField(default=expiry_date, editable=False)
    confirmed = models.BooleanField(default=False)
    kind = models.IntegerField(choices=ACCOUNT_CONFIRMATION_KIND, default=0)

    @property
    def is_expired(self):
        return self.expires < time.time()

    def __str__(self):
        return "AccountConfirmation %s, expired: %r" % \
            (self.user.email, self.is_expired())

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
    slug = models.SlugField()
    description = models.TextField()
    price = models.DecimalField(decimal_places=3, max_digits=65)
    invite_only = models.BooleanField(default=False)
    users = models.ManyToManyField(User, through='UserProductRelationship')
    revision = models.IntegerField(default=1)
    managed = models.BooleanField(default=True)
    management_url = models.URLField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return "Product %s" % self.name

class Domain(Product):
    domain_name = models.CharField(max_length=255)
    registrar = models.TextField()
    is_sub = models.BooleanField(default=False)

    @property
    def domain(self):
        return self.domain_name

    @domain.setter
    def domain(self, value):
        self.domain_name = value

    def __str__(self):
        return "Domain '%s'" % self.domain_name