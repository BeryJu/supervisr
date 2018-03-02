"""
Supervisr DNS record views
"""

from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.utils.translation import ugettext_lazy as _

from supervisr.core.models import UserAcquirableRelationship
from supervisr.core.views.generic import (GenericDeleteView, GenericReadView,
                                          GenericUpdateView)
from supervisr.core.views.wizards import BaseWizardView
from supervisr.dns.forms.resourcesets import ResourceSetForm
from supervisr.dns.models import ResourceSet


# pylint: disable=abstract-method
class ResourceSetReadView(GenericReadView):
    """View Resource Set"""

    model = ResourceSet
    template = 'dns/resourcesets/view.html'

    def get_instance(self):
        return self.model.objects.filter(uuid=self.kwargs.get('rset_uuid'),
                                         users__in=[self.request.user])

    def update_kwargs(self, kwargs):
        kwargs['records'] = kwargs.get('instance').resource.filter(
            users__in=[self.request.user])
        return kwargs


# pylint: disable=too-many-ancestors
class ResourceSetCreateView(BaseWizardView):
    """Wizard to create a new ResourceSet"""

    title = _('New Resource Set')
    form_list = [ResourceSetForm]

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        rset = form_dict['0'].save()
        UserAcquirableRelationship.objects.create(
            model=rset,
            user=self.request.user)
        messages.success(self.request, _('Resource Set successfully created'))
        return redirect(reverse('supervisr_dns:rset-view', kwargs={'rset_uuid': rset.uuid}))


class ResourceSetUpdateView(GenericUpdateView):
    """Update Resource Set"""

    model = ResourceSet
    model_verbose_name = _('Resource Set')
    form = ResourceSetForm

    def redirect(self, instance):
        return redirect(reverse('supervisr_dns:rset-view', kwargs={'rset_uuid': instance.uuid}))

    def get_instance(self):
        return ResourceSet.objects.filter(uuid=self.kwargs.get('rset_uuid'),
                                          users__in=[self.request.user])


class ResourceSetDeleteView(GenericDeleteView):
    """Delete Resource Set"""

    model = ResourceSet

    def redirect(self, instance):
        return redirect(reverse('supervisr_dns:dns-index'))

    def get_instance(self):
        return ResourceSet.objects.filter(uuid=self.kwargs.get('rset_uuid'),
                                          users__in=[self.request.user])
