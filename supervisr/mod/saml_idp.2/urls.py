
from django.conf.urls import url


from supervisr.mod.saml_idp.views.sso import SSO
from supervisr.mod.saml_idp.views.slo import SLO
from supervisr.mod.saml_idp.views.aidr import AIDR
from supervisr.mod.saml_idp.views.ars import ARS
from supervisr.mod.saml_idp.views.nmi import NMI
from supervisr.mod.saml_idp.views.nim import NIM
from supervisr.mod.saml_idp.views.aqs import AQS
from supervisr.mod.saml_idp.views.attr import ATTR

urlpatterns = [
    url(r'sso/post$', (SSO, "post")),
    url(r'sso/post/(.*)$', (SSO, "post")),
    url(r'sso/redirect$', (SSO, "redirect")),
    url(r'sso/redirect/(.*)$', (SSO, "redirect")),
    url(r'sso/art$', (SSO, "artifact")),
    url(r'sso/art/(.*)$', (SSO, "artifact")),
    # slo
    url(r'slo/redirect$', (SLO, "redirect")),
    url(r'slo/redirect/(.*)$', (SLO, "redirect")),
    url(r'slo/post$', (SLO, "post")),
    url(r'slo/post/(.*)$', (SLO, "post")),
    url(r'slo/soap$', (SLO, "soap")),
    url(r'slo/soap/(.*)$', (SLO, "soap")),
    #
    url(r'airs$', (AIDR, "uri")),
    url(r'ars$', (ARS, "soap")),
    # mni
    url(r'mni/post$', (NMI, "post")),
    url(r'mni/post/(.*)$', (NMI, "post")),
    url(r'mni/redirect$', (NMI, "redirect")),
    url(r'mni/redirect/(.*)$', (NMI, "redirect")),
    url(r'mni/art$', (NMI, "artifact")),
    url(r'mni/art/(.*)$', (NMI, "artifact")),
    url(r'mni/soap$', (NMI, "soap")),
    url(r'mni/soap/(.*)$', (NMI, "soap")),
    # nim
    url(r'nim$', (NIM, "soap")),
    url(r'nim/(.*)$', (NIM, "soap")),
    #
    url(r'aqs$', (AQS, "soap")),
    url(r'attr$', (ATTR, "soap")),
    url(r'verify?(.*)$', do_verify),
    url(r'sso/ecp$', (SSO, "ecp")),
]
