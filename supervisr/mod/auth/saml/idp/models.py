"""
Supervisr Auth SAML IDP Models
"""

from django.db import models

from supervisr.core.models import CreatedUpdatedModel
from supervisr.core.utils import class_to_path
from supervisr.mod.auth.saml.idp.base import Processor


class SAMLRemote(CreatedUpdatedModel):
    """
    Model to save information about a Remote SAML Endpoint
    """

    name = models.CharField(max_length=255, unique=True)
    acs_url = models.URLField()
    processor_path = models.CharField(max_length=255, choices=[])

    def __init__(self, *args, **kwargs):
        super(SAMLRemote, self).__init__(*args, **kwargs)
        processors = [(class_to_path(x), x.__name__) for x in Processor.__subclasses__()]
        self._meta.get_field('processor_path').choices = processors

    def __str__(self):
        return "SAMLRemote %s (processor=%s)" % (self.name, self.processor_path)
