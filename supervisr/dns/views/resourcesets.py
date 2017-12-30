"""
Supervisr DNS record views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.translation import ugettext_lazy as _

from supervisr.core.models import UserProductRelationship
from supervisr.core.views.generic import GenericDeleteView, GenericEditView
from supervisr.core.views.wizards import BaseWizardView
from supervisr.dns.forms.resourcesets import ResourceSetForm
from supervisr.dns.models import ResourceSet


@login_required
def view(request, rset_uuid):
    """View and edit ResourceSet"""
    res_set = get_object_or_404(ResourceSet, uuid=rset_uuid, users__in=[request.user])
    records = res_set.resource.filter(users__in=[request.user])

    return render(request, 'dns/resourcesets/view.html', {
        'rset': res_set,
        'records': records
    })

class ResourceSetNewView(BaseWizardView):
    """Wizard to create a new ResourceSet"""

    title = _('New Resource Set')
    form_list = [ResourceSetForm]

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        rset = form_dict['0'].save(commit=False)
        rset.save()
        UserProductRelationship.objects.create(
            product=rset,
            user=self.request.user)
        messages.success(self.request, _('Resource Set successfully created'))
        return redirect(reverse('supervisr/dns:rset-view', kwargs={'rset_uuid': rset.uuid}))

class ResourceSetEditView(GenericEditView):
    """Edit Resource Set"""

    model = ResourceSet
    model_verbose_name = _('Resource Set')
    form = ResourceSetForm

    def redirect(self, instance):
        return redirect(reverse('supervisr/dns:rset-view', kwargs={'rset_uuid': instance.uuid}))

    def get_instance(self):
        return ResourceSet.objects.filter(uuid=self.kwargs.get('rset_uuid'),
                                          users__in=[self.request.user])

class ResourceSetDeleteView(GenericDeleteView):
    """Delete Resource Set"""

    model = ResourceSet

    def redirect(self, instance):
        return redirect(reverse('supervisr/dns:dns-index'))

    def get_instance(self):
        return ResourceSet.objects.filter(uuid=self.kwargs.get('rset_uuid'),
                                          users__in=[self.request.user])
