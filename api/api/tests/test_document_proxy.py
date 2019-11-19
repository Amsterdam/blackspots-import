import logging
from unittest import skip
from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy
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
        self.document = mommy.make(
            Document,
            type='Ontwerp',
            filename='foo.pdf'
        )

    def test_setup(self):
        self.assertEqual(models.Spot.objects.count(), 1)
        self.assertEqual(models.Document.objects.count(), 1)

    @patch('objectstore_interaction.connection.get_blackspots_connection')
    @patch('objectstore_interaction.documents.get_actual_document')
    def test_get_document(self, get_mock, connection_mock):
        connection_mock.return_value = 'connection_object'
        get_mock.return_value = [
            {'content-type': 'application/pdf'},
            'blob'
        ]

        response = self.client.get(reverse('document-get-file', [self.document.id]))

        get_mock.assert_called_with('connection_object', 'doc/ontwerp', 'foo.pdf')
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/pdf', response['Content-Type'])
        self.assertEqual(response.content, b'blob')

    @patch('objectstore_interaction.connection.get_blackspots_connection')
    @patch('objectstore_interaction.documents.get_actual_document')
    def test_document_object_does_not_exist(self, get_mock, connection_mock):
        connection_mock.return_value = 'connection_object'
        get_mock.return_value = 'dontcare'
        get_mock.side_effect = ClientException('Something, something Object GET failed foo bar')

        response = self.client.get(reverse('document-get-file', [self.document.id]))

        self.assertEqual(404, response.status_code)

    @patch('objectstore_interaction.connection.get_blackspots_connection')
    @patch('objectstore_interaction.documents.get_actual_document')
    def test_objectstore_auth_error(self, get_mock, connection_mock):
        connection_mock.return_value = 'connection_object'
        get_mock.return_value = 'dontcare'
        get_mock.side_effect = ClientException('Something something Unauthorized foo bar')

        response = self.client.get(reverse('document-get-file', [self.document.id]))

        self.assertEqual(500, response.status_code)

    @patch('objectstore_interaction.connection.get_blackspots_connection')
    @patch('objectstore_interaction.documents.get_actual_document')
    def test_fail_other_client_exception(self, get_mock, connection_mock):
        connection_mock.return_value = 'connection_object'
        get_mock.return_value = 'dontcare'
        get_mock.side_effect = ClientException('Unknown error')

        response = self.client.get(reverse('document-get-file', [self.document.id]))

        self.assertEqual(500, response.status_code)
