"""supervisr mod beacon settings"""
from django.conf import settings

BEACON_ENABLED = not settings.DEBUG
BEACON_REMOTE = 'https://my.beryju.org'
