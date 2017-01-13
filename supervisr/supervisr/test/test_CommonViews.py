import os

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from ..models import get_system_user
from ..views import account, common


class CommonViewTestCase(TestCase):

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.factory = RequestFactory()

    def test_index_view(self):
        req = self.factory.get(reverse('common-index'))
        req.user = AnonymousUser()
        res = common.index(req)
        self.assertEqual(res.status_code, 302)

    def test_index_view_auth(self):
        req = self.factory.get(reverse('common-index'))
        req.user = User.objects.get(pk=get_system_user())
        res = common.index(req)
        self.assertEqual(res.status_code, 200)
