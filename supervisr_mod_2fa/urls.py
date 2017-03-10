"""
Supervisr Mod 2FA Urls
"""

from django.conf.urls import url

from .views import tfa

urlpatterns = [
    url(r'^$', tfa.index, name='tfa-index'),
    url(r'verify/$', tfa.verify, name='tfa-verify'),
    url(r'setup/$', tfa.setup, name='tfa-setup'),
]
