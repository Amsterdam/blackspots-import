"""Tests
"""

import logging

from django.test import TestCase
from model_mommy import mommy
from rest_framework.reverse import reverse

from datasets.blackspots import models
from datasets.blackspots.models import Spot, Document

log = logging.getLogger(__name__)


class TestAPIEndpoints(TestCase):
    """
    Verifies that browsing the API works correctly.
    """

    def setUp(self):
        for _ in range(3):
            mommy.make(Spot)

        self.spot_with_docs = mommy.make(Spot)
        for _ in range(3):
            mommy.make(Document, spot=self.spot_with_docs)

    def valid_response(self, url, response):
        """
        Helper method to check common status/json
        """

        self.assertEqual(
            200, response.status_code,
            'Wrong response code for {}'.format(url))

        self.assertEqual(
            'application/json', response['Content-Type'],
            'Wrong Content-Type for {}'.format(url))

    def test_setup(self):
        self.assertEqual(models.Spot.objects.count(), 4)
        self.assertEqual(models.Document.objects.count(), 3)

    def test_spot_list(self):
        url = reverse('spot-list')

        response = self.client.get(url)

        self.valid_response(url, response)
        data = response.data
        self.assertEqual(len(data), 4)
        spot_document_data = list(
            filter(lambda spot: spot.get('locatie_id') == self.spot_with_docs.locatie_id, data)
        )[0]
        self.assertEqual(len(spot_document_data.get('documents')), 3)

    def test_spot_list_geojson(self):
        url = reverse('spot-list', format='geojson')

        response = self.client.get(url)

        self.valid_response(url, response)
        data = response.data
        self.assertEqual(data.get('type'), 'FeatureCollection')
        self.assertEqual(len(data.get('features')), 4)

    def test_spot_detail(self):
        url = reverse('spot-detail', [self.spot_with_docs.locatie_id])

        response = self.client.get(url)

        self.valid_response(url, response)
        self.assertEqual(len(response.data.get('documents')), 3)

    def test_spot_detail_geojson(self):
        url = reverse('spot-detail', kwargs={
            'locatie_id': self.spot_with_docs.locatie_id,
            'format': 'geojson',
         })

        response = self.client.get(url)

        self.valid_response(url, response)
        self.assertEqual(response.data.get('type'), 'Feature')

    def test_documents_list(self):
        url = reverse('document-list')

        response = self.client.get(url)

        self.valid_response(url, response)
        self.assertEqual(len(response.data), 3)

    def test_documents_detail(self):
        url = reverse('document-detail', [1])

        response = self.client.get(url)

        self.valid_response(url, response)
