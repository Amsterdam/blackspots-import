import logging

from django.test import TestCase
from rest_framework.reverse import reverse

log = logging.getLogger(__name__)


class TestDocumentProxy(TestCase):
    """
    Verifies objectstore proxy working correctly
    """
    def test_swagger_yaml(self):
        url = reverse('swagger-schema', format='.yaml')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Blackspots API', str(response.content))

    def test_redoc_page(self):
        url = reverse('schema-redoc')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Blackspots API', str(response.content))
