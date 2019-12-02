import logging
from unittest import mock

from django.test import TestCase
from model_mommy import mommy
from model_mommy.recipe import seq
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from api.views import get_container_name
from datasets.blackspots import models
from datasets.blackspots.models import Document, Spot

log = logging.getLogger(__name__)


class TestAPIEndpoints(TestCase):
    """
    Verifies that browsing the API works correctly.
    """
    rest_client = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # use the DRF api client. See why:
        # https://www.django-rest-framework.org/api-guide/testing/#put-and-patch-with-form-data
        TestAPIEndpoints.rest_client = APIClient()

    def setUp(self):
        # generate 3 spots with locatie_ids test_1, test_2 and test_3
        mommy.make(Spot, locatie_id=seq('test_'), actiehouders="Unknown", _quantity=3)
        self.spot_with_docs = mommy.make(Spot)
        Document.objects.create(spot=self.spot_with_docs, type=Document.DocumentType.Ontwerp, filename='test')
        Document.objects.create(spot=self.spot_with_docs, type=Document.DocumentType.Rapportage, filename='test2')

    def tearDown(self):
        Document.objects.all().delete()
        Spot.objects.all().delete()

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
        self.assertEqual(models.Document.objects.count(), 2)

    def test_get_container_name(self):
        self.assertEqual(get_container_name(Document.DocumentType.Rapportage), 'doc/rapportage')
        self.assertEqual(get_container_name(Document.DocumentType.Ontwerp), 'doc/ontwerp')

    def test_spot_list(self):
        url = reverse('spot-list')

        response = self.rest_client.get(url)

        self.assertStatusCode(url, response)
        data = response.data
        self.assertEqual(data.get('count'), 4)
        spot_document_data = [
            spot for spot in data.get('results') if spot.get('locatie_id') == self.spot_with_docs.locatie_id
        ][0]
        self.assertEqual(len(spot_document_data.get('documents')), 2)

    def test_spot_list_geojson(self):
        url = reverse('spot-list', format='geojson')

        response = self.rest_client.get(url)

        self.assertStatusCode(url, response)
        data = response.data
        self.assertEqual(data.get('type'), 'FeatureCollection')
        self.assertEqual(len(data.get('features')), 4)

    def test_spot_detail_get(self):
        url = reverse('spot-detail', [self.spot_with_docs.locatie_id])
        response = self.rest_client.get(url)

        self.assertStatusCode(url, response)
        self.assertEqual(len(response.data.get('documents')), 2)

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
        url = reverse('spot-detail', ["test_1"])
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
        Spot.objects.create(**initial_data)

        url = reverse('spot-detail', [locatie_id])
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

        url = reverse('spot-detail', ["test_2"])
        response = self.rest_client.delete(url)
        self.assertStatusCode(url, response, expected_status=204)
        self.assertFalse(Spot.objects.filter(locatie_id='test_2').exists())

    def test_spot_detail_geojson(self):
        url = reverse('spot-detail', kwargs={
            'locatie_id': self.spot_with_docs.locatie_id,
            'format': 'geojson',
         })

        response = self.rest_client.get(url)

        self.assertStatusCode(url, response)
        self.assertEqual(response.data.get('type'), 'Feature')

    def test_documents_list(self):
        url = reverse('document-list')

        response = self.rest_client.get(url)

        self.assertStatusCode(url, response)
        self.assertEqual(response.data['count'], 2)
        
    def test_documents_detail(self):
        url = reverse('document-detail', [1])

        response = self.rest_client.get(url)

        self.assertStatusCode(url, response)
