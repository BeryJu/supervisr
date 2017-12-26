# from django.conf.urls import url, include
# from supervisr.core.models import BaseCredential
# from rest_framework import routers, serializers, viewsets

# # Serializers define the API representation.
# class CredentialSerializer(serializers.HyperlinkedModelSerializer):
#     """Serializer for BaseCredential"""

#     class Meta:
#         model = BaseCredential
#         exclude = []
#         # fields = ('username', 'password')

# # ViewSets define the view behavior.
# class CredentialViewSet(viewsets.ModelViewSet):
#     """ViewSet for Credential"""

#     queryset = BaseCredential.objects.all()
#     serializer_class = CredentialSerializer

#     def get_queryset(self):
#         return [x.cast() for x in BaseCredential.objects.filter(owner=self.request.user)]
"""Supervisr Core Credential APIv1"""

from supervisr.core.api.models import ModelAPI
from supervisr.core.models import BaseCredential, User
from supervisr.core.utils import path_to_class

def get_credential_forms():
    """Collect all credential forms in one list"""
    classes = BaseCredential.__subclasses__()
    forms = []
    for _sub in classes:
        if not getattr(_sub, 'form', None):
            print("Credential %s does not have form set")
            continue

        form_class = path_to_class(_sub.form)
        if form_class not in forms:
            forms.append(form_class)

    return forms

class CredentialAPI(ModelAPI):
    """
    Credential API
    """
    model = BaseCredential
    form = None

    def pre_handler(self, handler, request):
        self.form = get_credential_forms()
        return super(CredentialAPI, self).pre_handler(handler, request)

    def user_filter(self, queryset, user):
        """This method is used to check if the user has access"""
        qs = super(CredentialAPI, self).user_filter(queryset, user)
        return qs.filter(owner=user)
