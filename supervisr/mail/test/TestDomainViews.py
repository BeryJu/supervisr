"""
Supervisr Mail DomainView Test
"""

import os

from django.contrib.auth.models import User
from django.test import TestCase

from supervisr.core.models import (Domain, UserProductRelationship,
                                   get_system_user)
from supervisr.core.test.utils import test_request
from supervisr.mail.models import MailDomain
from supervisr.mail.views import domain


class TestDomainViews(TestCase):
    """
    Supervisr Mail DomainView Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        _domain = 'supervisr-unittest.beryju.org'
        self.ddomain = Domain.objects.create(domain=_domain, is_sub=True)
        self.user = User.objects.get(pk=get_system_user())
        UserProductRelationship.objects.create(user=self.user, product=self.ddomain)
        self.domain = MailDomain.objects.create(domain=self.ddomain)
        UserProductRelationship.objects.create(user=self.user, product=self.domain)

    def test_domain_view(self):
        """
        Test Index View (Anonymous)
        """
        self.assertEqual(test_request(domain.view, url_kwargs={
            'domain': self.domain.domain.domain
            }).status_code, 302)

    def test_domain_view_auth(self):
        """
        Test Index View (Authenticated)
        """
        self.assertEqual(test_request(domain.view, user=get_system_user(), url_kwargs={
            'domain': self.domain.domain.domain
            }).status_code, 200)

    def test_domain_view_404(self):
        """
        Test Index View (non-existant)
        """
        self.assertEqual(test_request(domain.view, user=get_system_user(), url_kwargs={
            'domain': 'invalid'
            }).status_code, 404)
