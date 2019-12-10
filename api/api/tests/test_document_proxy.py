import logging
from unittest.mock import patch

from django.test import TestCase
from model_bakery import baker
from rest_framework.reverse import reverse
from swiftclient import ClientException

from datasets.blackspots import models
from datasets.blackspots.models import Document

log = logging.getLogger(__name__)


class TestDocumentProxy(TestCase):
    """
    Verifies objectstore proxy working correctly
    """

    def setUp(self):
        self.document = baker.make(
            Document,
            type='Ontwerp',
            filename='foo.pdf'
        )

    def test_setup(self):
        self.assertEqual(models.Spot.objects.count(), 1)
        self.assertEqual(models.Document.objects.count(), 1)

    @patch('storage.objectstore.ObjectStore.get_connection')
    @patch('storage.objectstore.ObjectStore.get_document')
    def test_get_document(self, get_mock, connection_mock):
        connection_mock.return_value = 'connection_object'
        get_mock.return_value = [
            {'content-type': 'application/pdf'},
            'blob'
        ]

        response = self.client.get(reverse('document-get-file', [self.document.id]))

        # note, container name test is defined in the environment OBJECTSTORE_UPLOAD_CONTAINER_NAME
        get_mock.assert_called_with('connection_object', 'test/doc/ontwerp', 'foo.pdf')
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/pdf', response['Content-Type'])
        self.assertEqual(response.content, b'blob')

    @patch('storage.objectstore.ObjectStore.get_connection')
    @patch('storage.objectstore.ObjectStore.get_document')
    def test_document_object_does_not_exist(self, get_mock, connection_mock):
        connection_mock.return_value = 'connection_object'
        get_mock.return_value = 'dontcare'
        get_mock.side_effect = ClientException('Something, something Object GET failed foo bar')

        response = self.client.get(reverse('document-get-file', [self.document.id]))

        self.assertEqual(404, response.status_code)

    @patch('storage.objectstore.ObjectStore.get_connection')
    @patch('storage.objectstore.ObjectStore.get_document')
    def test_objectstore_auth_error(self, get_mock, connection_mock):
        connection_mock.return_value = 'connection_object'
        get_mock.return_value = 'dontcare'
        get_mock.side_effect = ClientException('Something something Unauthorized foo bar')

        response = self.client.get(reverse('document-get-file', [self.document.id]))

        self.assertEqual(500, response.status_code)

    @patch('storage.objectstore.ObjectStore.get_connection')
    @patch('storage.objectstore.ObjectStore.get_document')
    def test_fail_other_client_exception(self, get_mock, connection_mock):
        connection_mock.return_value = 'connection_object'
        get_mock.return_value = 'dontcare'
        get_mock.side_effect = ClientException('Unknown error')

        response = self.client.get(reverse('document-get-file', [self.document.id]))

        self.assertEqual(500, response.status_code)
