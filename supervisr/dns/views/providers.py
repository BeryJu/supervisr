from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from supervisr.core.models import ProviderInstance


class ProviderRenderView(View):
    """Render provider changes"""

    def get(self, request: HttpRequest) -> HttpResponse:
        providers = ProviderInstance.objects.filter(users__in=[request.user])
        dns_providers = []
        for instance in providers:
            if 'dns' in instance.provider.get_meta.get_capabilities():
                dns_providers.append(instance)
                dns_provider_inst = instance.provider.dns_provider(instance.credentials)
                print(dns_provider_inst.save(commit=False))
                # print(instance.provider.dns_provider.save(commit=False))
        return render(request, 'dns/providers/render.html', {
            'providers': dns_providers
        })
