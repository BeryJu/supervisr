"Helpers to add provider and account access information to the template context."
from __future__ import unicode_literals

from .models import Provider


def _get_enabled():
    """Wrapped function for filtering enabled providers."""
    providers = Provider.objects.all()
    return [p for p in providers if p.enabled()]


def available_providers():
    "Adds the list of enabled providers to the context."
    qs = Provider.objects.filter(consumer_secret__isnull=False, consumer_key__isnull=False)
    return {'oauth_providers': qs}
