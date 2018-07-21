"""supervisr mod web_proxy proxy tests"""

import threading
from wsgiref.simple_server import make_server
from wsgiref.validate import validator

from supervisr.core.tests.utils import TestCase, test_request
from supervisr.mod.web_proxy.models import WebApplication
from supervisr.mod.web_proxy.views import Proxy


class TestProxy(TestCase):
    """Test Proxy Views"""

    expected_result = b'test result'

    def setUp(self):
        super(TestProxy, self).setUp()

        # pylint: disable=unused-argument
        def simple_app(environ, start_response):
            """simple HTTP Server"""
            status = '200 OK'  # HTTP Status
            headers = [('Content-type', 'text/plain')]
            start_response(status, headers)

            return [self.expected_result]
        validator_app = validator(simple_app)

        self.httpd = make_server('', 0, validator_app)
        thread = threading.Thread(target=self.httpd.serve_forever)
        thread.daemon = True
        thread.start()

        WebApplication.objects.create(
            name='test',
            access_slug='test',
            upstream='http://%s:%d' % self.httpd.server_address
        )

    def test_reverse_proxy(self):
        """Test fundamental reverse proxy"""
        response = test_request(Proxy.as_view(), url_kwargs={
            'slug': 'test',
            'path': '/'
        }, user=self.system_user)
        self.assertEqual(list(response.streaming_content)[0], self.expected_result)
        self.assertEqual(response.status_code, 200)

    def test_reverse_proxy_unauth(self):
        """Test fundamental reverse proxy (without authentication)"""
        self.assertEqual(test_request(Proxy.as_view(), url_kwargs={
            'slug': 'test',
            'path': '/'
        }).status_code, 404)

    def test_reverse_proxy_invalid(self):
        """Test fundamental reverse proxy (invalid upstream)"""
        WebApplication.objects.create(
            name='invalid',
            access_slug='invalid',
            upstream='http://localhost:1'
        )
        self.assertEqual(test_request(Proxy.as_view(), url_kwargs={
            'slug': 'invalid',
            'path': '/'
        }, user=self.system_user).status_code, 500)

    def tearDown(self):
        self.httpd.shutdown()
