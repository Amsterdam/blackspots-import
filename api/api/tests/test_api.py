import logging
from unittest import mock

from django.test import TestCase
from model_mommy import mommy
from model_mommy.recipe import seq
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from datasets.blackspots import models
from datasets.blackspots.models import Document, Spot

log = logging.getLogger(__name__)


class TestAPIEndpoints(TestCase):
    """
    Verifies that browsing the API works correctly.
    """

    def setUp(self):
        # use the DRF api client. See why:
        # https://www.django-rest-framework.org/api-guide/testing/#put-and-patch-with-form-data
        self.rest_client = APIClient()

        # generate 3 spots with locatie_ids test_1, test_2 and test_3
        mommy.make(Spot, locatie_id=seq('test_'), actiehouders="Unknown", _quantity=3)
        self.spot_with_docs = mommy.make(Spot)
        mommy.make(Document, spot=self.spot_with_docs, _quantity=3)

    def assertStatusCode(self, url, response, expected_status=200):
        """
        Helper method to check common status/json
        """
        self.assertEqual(expected_status, response.status_code,
                         f'Wrong response code for {url}. \n\nContent: {response.content}. \n\n'
                         f'Headers: {response.serialize_headers()}')

        if expected_status != 204:
            self.assertEqual(
                'application/json', response['Content-Type'],
                'Wrong Content-Type for {}'.format(url))

    def test_setup(self):
        self.assertEqual(models.Spot.objects.count(), 4)
        self.assertEqual(models.Document.objects.count(), 3)

    def test_spot_list(self):
        url = reverse('spot-list')

        response = self.rest_client.get(url)

        self.assertStatusCode(url, response)
        data = response.data
        self.assertEqual(data.get('count'), 4)
        spot_document_data = [
            spot for spot in data.get('results') if spot.get('locatie_id') == self.spot_with_docs.locatie_id
        ][0]
        self.assertEqual(len(spot_document_data.get('documents')), 3)

    def test_spot_list_geojson(self):
        url = reverse('spot-list', format='geojson')

        response = self.rest_client.get(url)

        self.assertStatusCode(url, response)
        data = response.data
        self.assertEqual(data.get('type'), 'FeatureCollection')
        self.assertEqual(len(data.get('features')), 4)

    def test_spot_detail_get(self):
        url = reverse('spot-detail', [self.spot_with_docs.id])
        response = self.rest_client.get(url)

        self.assertStatusCode(url, response)
        self.assertEqual(len(response.data.get('documents')), 3)

    @mock.patch('api.serializers.SpotSerializer.determine_stadsdeel')
    def test_spot_detail_post(self, determine_stadsdeel):
        determine_stadsdeel.return_value = Spot.Stadsdelen.Centrum

        url = reverse('spot-list')
        data = {
            'locatie_id': '123',
            'spot_type': Spot.SpotType.blackspot,
            'description': 'Test spot',
            'point': '{"type": "Point","coordinates": [4.9239022,52.3875654]}',
            'actiehouders': 'Actiehouders test',
            'status': 'voorbereiding',
            'jaar_blackspotlijst': 2019
        }
        response = self.rest_client.post(url, data=data)
        self.assertStatusCode(url, response, expected_status=201)

        del data['point']
        self.assertTrue(Spot.objects.filter(**data).exists())

    def test_spot_detail_patch(self):
        spot = Spot.objects.get(locatie_id='test_1')
        url = reverse('spot-detail', [spot.id])
        data = {
            'actiehouders': 'Someone',
        }
        response = self.rest_client.patch(url, data=data)
        self.assertStatusCode(url, response)
        self.assertTrue(Spot.objects.filter(actiehouders='Someone', locatie_id='test_1').exists())

    @mock.patch('api.serializers.SpotSerializer.determine_stadsdeel')
    def test_spot_detail_put(self, determine_stadsdeel):
        determine_stadsdeel.return_value = Spot.Stadsdelen.Centrum

        locatie_id = 'abcdef'
        initial_data = {
            'locatie_id': locatie_id,
            'spot_type': Spot.SpotType.blackspot,
            'description': 'TEST PUT',
            'point': '{"type": "Point","coordinates": [123, 456]}',
            'actiehouders': 'PUT actiehouders',
            'status': 'voorbereiding',
            'jaar_blackspotlijst': 2019
        }
        created_spot = Spot.objects.create(**initial_data)

        url = reverse('spot-detail', [created_spot.id])
        new_data = {
            'locatie_id': locatie_id,
            'spot_type': Spot.SpotType.risico,
            'description': 'TEST PUT 2',
            'point': '{"type": "Point","coordinates": [567, 789]}',
            'actiehouders': 'PUT actiehouders 2',
            'status': 'gereed'
        }
        response = self.rest_client.put(url, data=new_data)
        self.assertStatusCode(url, response)

        del initial_data['point']
        del new_data['point']
        self.assertFalse(Spot.objects.filter(**initial_data).exists())
        self.assertTrue(Spot.objects.filter(**new_data).exists())

    def test_spot_detail_delete(self):
        self.assertTrue(Spot.objects.filter(locatie_id='test_2').exists())
        spot = Spot.objects.get(locatie_id='test_2')

        url = reverse('spot-detail', [spot.id])
        response = self.rest_client.delete(url)
        self.assertStatusCode(url, response, expected_status=204)
        self.assertFalse(Spot.objects.filter(locatie_id='test_2').exists())

    def test_spot_detail_geojson(self):
        url = reverse('spot-detail', kwargs={
            'id': self.spot_with_docs.id,
            'format': 'geojson',
         })

        response = self.rest_client.get(url)

        self.assertStatusCode(url, response)
        self.assertEqual(response.data.get('type'), 'Feature')

    def test_documents_list(self):
        url = reverse('document-list')

        response = self.rest_client.get(url)

        self.assertStatusCode(url, response)
        self.assertEqual(len(response.data), 3)

    def test_documents_detail(self):
        url = reverse('document-detail', [1])

        response = self.rest_client.get(url)

        self.assertStatusCode(url, response)
