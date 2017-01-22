"""
Core Modules for supervisr
"""
from __future__ import unicode_literals

import base64
import json
import math
import random
import time
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import AppRegistryNotReady, ObjectDoesNotExist
from django.db import models
from django.db.models import Max
from django.db.utils import OperationalError
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _

from .signals import (SIG_USER_PRODUCT_RELATIONSHIP_CREATED,
                      SIG_USER_PRODUCT_RELATIONSHIP_DELETED)

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
    """
    Return the default expiry for AccountConfirmations
    """
    return time.time() + 172800 # 2 days

def get_username():
    """
    Generate a completely random 10-char user_name (used for unix-accounts)
    """
    # Generate a normal UUID, convert it to base64 and take the 10 first chars
    uid = uuid.uuid4()
    # UUID in base64 is 25 chars, we want 10 char length
    offset = random.randint(0, 15)
    # Python3 changed the way we need to encode
    res = base64.b64encode(uid.bytes, altchars=b'_-')
    return res[offset:offset+10]

def get_userid():
    """
    Get the next higher unix user_id, since we can't set the start for django's AutoField
    """
    # Custom default to set the unix_userid since we can't have an
    # AutoField as non-primary-key. Also so we can set a custom start,
    # which is settings.USER_PROFILE_ID_START
    try:
        highest = UserProfile.objects.all.aggregate(Max('unix_userid'))
        return highest + 1
    except (AppRegistryNotReady, ObjectDoesNotExist, AttributeError):
        return settings.USER_PROFILE_ID_START

def get_system_user():
    """
    Return supervisr's System User PK. This is created with the initial Migration,
    but might not be ID 1
    """
    system_users = User.objects.filter(username=settings.SYSTEM_USER_NAME)
    if system_users.exists():
        return system_users[0].id
    else:
        return 1 # Django starts AutoField's with 1 not 0

class UserProfile(models.Model):
    """
    Save settings associated with user, since we don't want a custom user Model
    """
    user = models.OneToOneField(User, primary_key=True)
    unix_username = models.CharField(max_length=10, default=get_username, editable=False)
    unix_userid = models.IntegerField(default=get_userid)
    locale = models.CharField(max_length=5, default='en-US')

    def __str__(self):
        return "UserProfile %s" % self.user.email

class Setting(models.Model):
    """
    Save key-value settings to db
    """
    key = models.CharField(max_length=255, primary_key=True)
    value = models.TextField()

    @property
    def value_bool(self):
        """
        Return value converted to boolean
        """
        return self.value.lower() == 'true'

    def set_bool(self, value):
        """
        Set value from boolean
        """
        self.value = str(value)

    def __str__(self):
        return "Setting %s" % self.key

    @staticmethod
    def get(key, default=''):
        """
        Get value, when Setting doesn't exist, it's created with default
        """
        try:
            setting = Setting.objects.get_or_create(
                key=key,
                defaults={'value': default})[0]
            return setting.value
        except OperationalError:
            return default

    @staticmethod
    def set(key, value):
        """
        Set value, when Setting doesn't exist, it's created with value
        """
        setting, created = Setting.objects.get_or_create(
            key=key,
            defaults={'value': value})
        if created is False:
            setting.value = value
            setting.save()

class AccountConfirmation(models.Model):
    """
    Save information about actions that need to be confirmed
    """
    account_confirmation_id = models.UUIDField(primary_key=True, \
        default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)
    expires = models.BigIntegerField(default=expiry_date, editable=False)
    confirmed = models.BooleanField(default=False)
    kind = models.IntegerField(choices=ACCOUNT_CONFIRMATION_KIND, default=0)

    @property
    def is_expired(self):
        """
        Returns whether or not the confirmation is expired or not
        """
        return self.expires < time.time()

    def __str__(self):
        return "AccountConfirmation %s, expired: %r" % \
            (self.user.email, self.is_expired)

class UserProductRelationship(models.Model):
    """
    Keeps track of a relationship between a User and a Product, with optional instance informations
    """
    user_product_relationship_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    product = models.ForeignKey('Product')
    instance_name = models.TextField(blank=True, null=True)
    expiry_delta = models.BigIntegerField(default=0)
    discount_percent = models.IntegerField(default=0)

    @property
    def name(self):
        """
        Returns the instance_name if set, otherwise the product name
        """
        if self.instance_name:
            return self.instance_name
        return self.product.name

    def __str__(self):
        return _("UserProductRelationship %(product)s %(user)s" % {
            'user': self.user,
            'product': self.product,
            })

    def save(self, *args, **kwargs):
        if self.pk is None:
            # Trigger event that we were saved
            SIG_USER_PRODUCT_RELATIONSHIP_CREATED.send(
                sender=UserProductRelationship,
                upr=self)
        super(UserProductRelationship, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Send signal to we are going to be deleted
        SIG_USER_PRODUCT_RELATIONSHIP_DELETED.send(
            sender=UserProductRelationship,
            upr=self)
        # Set all other events from us to current=False
        events = Event.objects.filter(
            product=self.product,
            user=self.user)
        if events.exists():
            for event in events:
                event.current = False
                event.save()
        super(UserProductRelationship, self).delete(*args, **kwargs)

class Product(models.Model):
    """
    Information about the Main Product itself. This instances of this classes
    are assumed to be managed services.
    """
    product_id = models.AutoField(primary_key=True)
    name = models.TextField()
    slug = models.SlugField()
    description = models.TextField()
    price = models.DecimalField(decimal_places=3, max_digits=65)
    invite_only = models.BooleanField(default=False)
    auto_add = models.BooleanField(default=False)
    auto_all_add = models.BooleanField(default=False)
    users = models.ManyToManyField(User, through='UserProductRelationship')
    revision = models.IntegerField(default=1)
    managed = models.BooleanField(default=True)
    management_url = models.URLField(max_length=1000, blank=True, null=True)
    ldap_group = models.TextField(blank=True, help_text=('This is an optional field for a LDAP '
                                                         'Group DN, to which the user is added once'
                                                         ' they have a relationship with '
                                                         'the Product.'))

    def __str__(self):
        return "Product %s" % self.name

    @staticmethod
    def do_auto_add(user):
        """
        Auto-associates Product with new users. We have a separate function for
        this since we use the default Django User Model.
        """
        to_add = Product.objects.filter(auto_add=True)
        for product in to_add:
            UserProductRelationship.objects.create(
                user=user,
                product=product)

    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)
        if self.auto_all_add is True:
            # Since there is no better way to do the query other way roundd
            # We have to do it like this
            rels = list(UserProductRelationship.objects.filter(product=self))
            rels_userlist = []
            users = list(User.objects.all())
            for rel in rels:
                rels_userlist.append(rel.user)
            missing_users = set(rels_userlist).symmetric_difference(set(users))
            for missing_user in missing_users:
                UserProductRelationship.objects.create(
                    user=missing_user,
                    product=self)

class Domain(Product):
    """
    Information about a Domain, which is used for other sub-apps.
    This is also used for sub domains, hence the is_sub.
    """
    registrar = models.TextField()
    is_sub = models.BooleanField(default=False)

    @property
    def domain(self):
        """
        Wrapper so we can do domain.domain
        """
        return self.name

    @domain.setter
    def domain(self, value):
        """
        Wrapper so we can do domain.domain
        """
        self.name = value

    def __str__(self):
        return "Domain '%s'" % self.domain_name

class Event(models.Model):
    """
    Store information about important Event's for auditing, like signing up, changing/resetting
    your password or gaining access to a new Product
    """
    event_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    glyph = models.CharField(max_length=200, default='envelope')
    message = models.TextField()
    current = models.BooleanField(default=True)
    action_required = models.BooleanField(default=False)
    action_view = models.TextField()
    action_parmas_json = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    closed_date = models.DateTimeField(auto_now=True)
    invoker = models.ForeignKey(User, default=get_system_user, related_name='events_invoked')
    hidden = models.BooleanField(default=False)
    send_notification = models.BooleanField(default=False)
    remote_ip = models.GenericIPAddressField(default='0.0.0.0')
    remote_ip_rdns = models.TextField(default='')

    @property
    def action_parmas(self):
        """
        Return action's params as dict
        """
        return json.loads(self.action_parmas_json)

    @action_parmas.setter
    def action_params(self, value):
        """
        Set action's params from a dict and saves it as json
        """
        self.action_parmas_json = json.dumps(value)

    @property
    def get_url(self):
        """
        Returns relative url for action with params
        """
        return reverse(self.action_view, kwargs=self.action_parmas)

    @property
    def get_localized_age(self):
        """
        Return age as a localized String
        """
        now = timezone.now()
        diff = now - self.create_date
        hours = int(diff.seconds / 3600)
        minutes = int(math.ceil(diff.seconds / 60))
        if diff.days > 0:
            return _("%(days)d day(s) ago" % {'days': diff.days})
        elif hours > 0:
            return _("%(hours)d hour(s) ago" % {'hours': hours})
        else:
            return _("%(minutes)d minute(s) ago" % {'minutes': minutes})

    def __str__(self):
        return "Event '%s' '%s'" % (self.user.username, self.message)
