"""
Supervisr DNS record views
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils.translation import ugettext_lazy as _

from supervisr.core.models import UserProductRelationship
from supervisr.core.views.generic import GenericDeleteView, GenericUpdateView
from supervisr.core.views.wizards import BaseWizardView
from supervisr.dns.forms.recordresource import RecordResourceForm
from supervisr.dns.models import RecordResource, ResourceSet


class RecordResourceCreateView(BaseWizardView):
    """Wizard to create a new RecordResource"""

    title = _('New Record Resource')
    form_list = [RecordResourceForm]

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        rset_uuid = self.kwargs.get('rset_uuid')
        rset = get_object_or_404(ResourceSet, uuid=rset_uuid, users__in=[self.request.user])
        rres = form_dict['0'].save(commit=False)
        rres.save()
        rset.resource.add(rres)
        UserProductRelationship.objects.create(
            product=rres,
            user=self.request.user)
        messages.success(self.request, _('Record Resource successfully created'))
        return redirect(reverse('supervisr/dns:rset-read', kwargs={'rset_uuid': rset.uuid}))

class RecordResourceUpdateView(GenericUpdateView):
    """Update Record Resource"""

    model = RecordResource
    model_verbose_name = _('Record Resource')
    form = RecordResourceForm

    def redirect(self, instance):
        return redirect(reverse('supervisr/dns:rset-read', kwargs={'rset_uuid': instance.uuid}))

    def get_instance(self):
        return RecordResource.objects.filter(uuid=self.kwargs.get('rset_uuid'),
                                             users__in=[self.request.user])

class RecordResourceDeleteView(GenericDeleteView):
    """Delete Record Resource"""

    model = RecordResource

    def redirect(self, instance):
        return redirect(reverse('supervisr/dns:rset-read', kwargs={'rset_uuid': instance.uuid}))

    def get_instance(self):
        return RecordResource.objects.filter(uuid=self.kwargs.get('rset_uuid'),
                                             users__in=[self.request.user])
