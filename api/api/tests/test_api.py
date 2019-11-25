import logging

from django.test import TestCase
from model_mommy import mommy
from rest_framework.reverse import reverse

from datasets.blackspots import models
from datasets.blackspots.models import Document, Spot

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

    def assertStatusCode(self, url, response, expected_status=200):
        """
        Helper method to check common status/json
        """
        content = response.content if not response.streaming else "*http stream*"
        self.assertEqual(expected_status, response.status_code,
                         f'Wrong response code for {url}. \n\nContent: {content}. \n\n'
                         f'Headers: {response.serialize_headers()}')

        self.assertEqual(
            'application/json', response['Content-Type'],
            'Wrong Content-Type for {}'.format(url))

    def test_setup(self):
        self.assertEqual(models.Spot.objects.count(), 4)
        self.assertEqual(models.Document.objects.count(), 3)

    def test_spot_list(self):
        url = reverse('spot-list')

        response = self.client.get(url)

        self.assertStatusCode(url, response)
        data = response.data
        self.assertEqual(data.get('count'), 4)
        spot_document_data = [
            spot for spot in data.get('results') if spot.get('locatie_id') == self.spot_with_docs.locatie_id
        ][0]
        self.assertEqual(len(spot_document_data.get('documents')), 3)

    def test_spot_list_geojson(self):
        url = reverse('spot-list', format='geojson')

        response = self.client.get(url)

        self.assertStatusCode(url, response)
        data = response.data
        self.assertEqual(data.get('type'), 'FeatureCollection')
        self.assertEqual(len(data.get('features')), 4)

    def test_spot_detail_get(self):
        url = reverse('spot-detail', [self.spot_with_docs.locatie_id])
        response = self.client.get(url)

        self.assertStatusCode(url, response)
        self.assertEqual(len(response.data.get('documents')), 3)

    def test_spot_detail_post(self):
        url = reverse('spot-list')
        data = {
            'locatie_id': '123',
            'spot_type': Spot.SpotType.blackspot,
            'description': 'Test spot',
            'point': '{"type": "Point","coordinates": [4.9239022,52.3875654]}',
            'actiehouders': 'Actiehouders test'
        }
        response = self.client.post(url, data=data)
        self.assertStatusCode(url, response, expected_status=201)

        del data['point']
        self.assertTrue(Spot.objects.filter(**data).exists())

    def test_spot_detail_geojson(self):
        url = reverse('spot-detail', kwargs={
            'locatie_id': self.spot_with_docs.locatie_id,
            'format': 'geojson',
         })

        response = self.client.get(url)

        self.assertStatusCode(url, response)
        self.assertEqual(response.data.get('type'), 'Feature')

    def test_documents_list(self):
        url = reverse('document-list')

        response = self.client.get(url)

        self.assertStatusCode(url, response)
        self.assertEqual(len(response.data), 3)

    def test_documents_detail(self):
        url = reverse('document-detail', [1])

        response = self.client.get(url)

        self.assertStatusCode(url, response)
