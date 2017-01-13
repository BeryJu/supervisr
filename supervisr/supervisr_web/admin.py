from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from supervisr.admin import admin_autoregister

admin_autoregister('supervisr_web')
