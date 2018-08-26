"""Supervisr DNS resource views"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils.translation import ugettext_lazy as _

from supervisr.core.models import UserAcquirableRelationship
from supervisr.core.views.generic import GenericDeleteView, GenericUpdateView
from supervisr.core.views.wizards import BaseWizardView
from supervisr.dns.forms.resource import ResourceForm
from supervisr.dns.models import Resource, ResourceSet


# pylint: disable=too-many-ancestors
class ResourceCreateView(BaseWizardView):
    """Wizard to create a new Resource"""

    title = _('New Record Resource')
    form_list = [ResourceForm]

    def finish(self, form_list):
        rset_uuid = self.kwargs.get('rset_uuid')
        rset = get_object_or_404(ResourceSet, uuid=rset_uuid, users__in=[self.request.user])
        resource = form_list[0].save()
        rset.resource.add(resource)
        UserAcquirableRelationship.objects.create(
            model=resource,
            user=self.request.user)
        messages.success(self.request, _('Record Resource successfully created'))
        return redirect(reverse('supervisr_dns:rset-view', kwargs={'rset_uuid': rset.uuid}))


class ResourceUpdateView(GenericUpdateView):
    """Update Record Resource"""

    model = Resource
    model_verbose_name = _('Record Resource')
    form = ResourceForm

    def redirect(self, instance):
        return 'supervisr_dns:index'

    def get_instance(self):
        return Resource.objects.filter(uuid=self.kwargs.get('resource_uuid'),
                                       users__in=[self.request.user])


class ResourceDeleteView(GenericDeleteView):
    """Delete Record Resource"""

    model = Resource

    def redirect(self, instance):
        return 'supervisr_dns:index'

    def get_instance(self):
        return Resource.objects.filter(uuid=self.kwargs.get('resource_uuid'),
                                       users__in=[self.request.user])
