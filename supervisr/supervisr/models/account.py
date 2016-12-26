from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
import uuid
import time

class AccountConfirmation(object):
    account_confirmation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)
    expires = models.BigIntegerField()
    confirmed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(AccountConfirmation, self).save(*args, **kwargs)
        if self.pk is None:
            self.expires = time.time() + 172800 # 2 days
