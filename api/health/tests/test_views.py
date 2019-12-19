from unittest import mock

from django.test import TestCase, override_settings


class TestViews(TestCase):

    def test_health_view(self):
        response = self.client.get('/status/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Connectivity OK")

    @override_settings(DEBUG=True)
    def test_debug(self):
        response = self.client.get('/status/health')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, b"Debug mode not allowed in production")

    @mock.patch("health.views.connection.cursor")
    def test_database_error(self, mocked_cursor):
        mocked_cursor.side_effect = Exception
        response = self.client.get('/status/health')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, b"Database connectivity failed")
