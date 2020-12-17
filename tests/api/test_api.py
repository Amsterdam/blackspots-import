import logging
from unittest import mock

from django.test import TransactionTestCase
from model_bakery import baker, seq
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from datasets.blackspots import models
from datasets.blackspots.models import Document, Spot
from tests.api.authzsetup import AuthorizationSetup

log = logging.getLogger(__name__)


class TestAPIEndpoints(TransactionTestCase, AuthorizationSetup):
    """
    Verifies that browsing the API works correctly.
    """
    reset_sequences = True

    def setUp(self):
        self.setup_clients()

        # generate 3 spots with locatie_ids test_1, test_2 and test_3
        baker.prepare(Document)  # because of this line the next bakery will work
        baker.make(Spot, locatie_id=seq("test_"), actiehouders="Unknown", _quantity=3)
        self.spot_with_docs = baker.make(Spot)
        baker.make(Document, spot=self.spot_with_docs, _quantity=3)

    def assertStatusCode(self, url, response, expected_status=200):
        """
        Helper method to check common status/json
        """
        self.assertEqual(
            expected_status,
            response.status_code,
            f"Wrong response code for {url}. \n\nContent: {response.content}. \n\n"
            f"Headers: {response.serialize_headers()}",
        )

        if expected_status < 300 and expected_status != 204:
            # test content type if expected status is non error and other
            # than no content (204)
            self.assertEqual(
                "application/json",
                response["Content-Type"],
                "Wrong Content-Type for {}".format(url),
            )

    def test_setup(self):
        self.assertEqual(models.Spot.objects.count(), 4)
        self.assertEqual(models.Document.objects.count(), 3)

    def test_spot_list(self):
        url = reverse("spot-list")

        response = self.read_client.get(url)

        self.assertStatusCode(url, response)
        data = response.data
        self.assertEqual(data.get("count"), 4)
        spot_document_data = [
            spot
            for spot in data.get("results")
            if spot.get("locatie_id") == self.spot_with_docs.locatie_id
        ][0]
        self.assertEqual(len(spot_document_data.get("documents")), 3)

    def test_spot_list_auth_error(self):
        url = reverse("spot-list")

        for client in [self.anon_client, self.write_client]:
            response = client.get(url)
            self.assertStatusCode(url, response, 401)

    def test_spot_list_geojson(self):
        url = reverse("spot-list", format="geojson")

        response = self.read_client.get(url)

        self.assertStatusCode(url, response)
        data = response.data
        self.assertEqual(data.get("type"), "FeatureCollection")
        self.assertEqual(len(data.get("features")), 4)

    def test_spot_list_geojson_auth_error(self):
        url = reverse("spot-list", format="geojson")

        for client in [self.anon_client, self.write_client]:
            response = client.get(url)
            self.assertStatusCode(url, response, 401)

    def test_spot_detail_get(self):
        url = reverse("spot-detail", [self.spot_with_docs.id])
        response = self.read_client.get(url)

        self.assertStatusCode(url, response)
        self.assertEqual(len(response.data.get("documents")), 3)

    def test_spot_detail_get_auth_error(self):
        url = reverse("spot-detail", [self.spot_with_docs.id])

        for client in [self.anon_client, self.write_client]:
            response = client.get(url)
            self.assertStatusCode(url, response, 401)

    @mock.patch("api.serializers.SpotSerializer.determine_stadsdeel")
    def test_spot_detail_post(self, determine_stadsdeel):
        determine_stadsdeel.return_value = Spot.Stadsdelen.Centrum

        url = reverse("spot-list")
        data = {
            "locatie_id": "123",
            "spot_type": Spot.SpotType.blackspot,
            "description": "Test spot",
            "point": '{"type": "Point","coordinates": [4.9239022,52.3875654]}',
            "actiehouders": "Actiehouders test",
            "status": "voorbereiding",
            "jaar_blackspotlijst": 2019,
        }
        response = self.write_client.post(url, data=data)
        self.assertStatusCode(url, response, expected_status=201)

        del data["point"]
        self.assertTrue(Spot.objects.filter(**data).exists())

    @mock.patch("api.serializers.SpotSerializer.determine_stadsdeel")
    def test_spot_detail_post_auth_error(self, determine_stadsdeel):
        determine_stadsdeel.return_value = Spot.Stadsdelen.Centrum

        url = reverse("spot-list")
        for client in [self.anon_client, self.read_client]:
            data = {
                "locatie_id": "12345",
                "spot_type": Spot.SpotType.blackspot,
                "description": "Test spot",
                "point": '{"type": "Point","coordinates": [4.9239022,52.3875654]}',
                "actiehouders": "Actiehouders test",
                "status": "voorbereiding",
                "jaar_blackspotlijst": 2019,
            }
            response = client.post(url, data=data)
            self.assertStatusCode(url, response, expected_status=401)

            del data["point"]
            self.assertFalse(Spot.objects.filter(**data).exists())

    def test_spot_detail_patch(self):
        spot = Spot.objects.get(locatie_id="test_1")
        url = reverse("spot-detail", [spot.id])
        data = {
            "actiehouders": "Someone",
        }
        response = self.write_client.patch(url, data=data)
        self.assertStatusCode(url, response)
        self.assertTrue(
            Spot.objects.filter(actiehouders="Someone", locatie_id="test_1").exists()
        )

    def test_spot_detail_patch_auth_error(self):
        spot = Spot.objects.get(locatie_id="test_1")
        url = reverse("spot-detail", [spot.id])
        data = {
            "actiehouders": "Someone foobar",
        }

        for client in [self.anon_client, self.read_client]:
            response = client.patch(url, data=data)
            self.assertStatusCode(url, response, 401)
            self.assertFalse(
                Spot.objects.filter(actiehouders="Someone foobar", locatie_id="test_1").exists()
            )

    @mock.patch("api.serializers.SpotSerializer.determine_stadsdeel")
    def test_spot_detail_put(self, determine_stadsdeel):
        determine_stadsdeel.return_value = Spot.Stadsdelen.Centrum

        locatie_id = "abcdef"
        initial_data = {
            "locatie_id": locatie_id,
            "spot_type": Spot.SpotType.blackspot,
            "description": "TEST PUT",
            "point": '{"type": "Point","coordinates": [123, 456]}',
            "actiehouders": "PUT actiehouders",
            "status": "voorbereiding",
            "jaar_blackspotlijst": 2019,
        }
        created_spot = Spot.objects.create(**initial_data)

        url = reverse("spot-detail", [created_spot.id])
        new_data = {
            "locatie_id": locatie_id,
            "spot_type": Spot.SpotType.risico,
            "description": "TEST PUT 2",
            "point": '{"type": "Point","coordinates": [567, 789]}',
            "actiehouders": "PUT actiehouders 2",
            "status": "gereed",
        }
        response = self.write_client.put(url, data=new_data)
        self.assertStatusCode(url, response)

        del initial_data["point"]
        del new_data["point"]
        self.assertFalse(Spot.objects.filter(**initial_data).exists())
        self.assertTrue(Spot.objects.filter(**new_data).exists())

    @mock.patch("api.serializers.SpotSerializer.determine_stadsdeel")
    def test_spot_detail_put_auth_error(self, determine_stadsdeel):
        determine_stadsdeel.return_value = Spot.Stadsdelen.Centrum

        locatie_id = "abcdef"
        initial_data = {
            "locatie_id": locatie_id,
            "spot_type": Spot.SpotType.blackspot,
            "description": "TEST PUT",
            "point": '{"type": "Point","coordinates": [123, 456]}',
            "actiehouders": "PUT actiehouders",
            "status": "voorbereiding",
            "jaar_blackspotlijst": 2019,
        }
        created_spot = Spot.objects.create(**initial_data)
        del initial_data["point"]

        url = reverse("spot-detail", [created_spot.id])
        for client in [self.anon_client, self.read_client]:
            new_data = {
                "locatie_id": locatie_id,
                "spot_type": Spot.SpotType.risico,
                "description": "TEST PUT 2",
                "point": '{"type": "Point","coordinates": [567, 789]}',
                "actiehouders": "PUT actiehouders 2",
                "status": "gereed",
            }

            response = client.put(url, data=new_data)
            self.assertStatusCode(url, response, 401)
            del new_data["point"]
            self.assertTrue(Spot.objects.filter(**initial_data).exists())
            self.assertFalse(Spot.objects.filter(**new_data).exists())

    def test_spot_detail_delete(self):
        self.assertTrue(Spot.objects.filter(locatie_id="test_2").exists())
        spot = Spot.objects.get(locatie_id="test_2")

        url = reverse("spot-detail", [spot.id])
        response = self.write_client.delete(url)
        self.assertStatusCode(url, response, expected_status=204)
        self.assertFalse(Spot.objects.filter(locatie_id="test_2").exists())

    def test_spot_detail_delete_auth_error(self):
        self.assertTrue(Spot.objects.filter(locatie_id="test_2").exists())
        spot = Spot.objects.get(locatie_id="test_2")

        url = reverse("spot-detail", [spot.id])
        for client in [self.anon_client, self.read_client]:
            response = client.delete(url)
            self.assertStatusCode(url, response, expected_status=401)
            self.assertTrue(Spot.objects.filter(locatie_id="test_2").exists())

    def test_spot_detail_geojson(self):
        url = reverse(
            "spot-detail", kwargs={"id": self.spot_with_docs.id, "format": "geojson",}
        )

        response = self.read_client.get(url)
        self.assertStatusCode(url, response)
        self.assertEqual(response.data.get("type"), "Feature")

    def test_spot_detail_geojson_auth_error(self):
        url = reverse(
            "spot-detail", kwargs={"id": self.spot_with_docs.id, "format": "geojson",}
        )

        for client in [self.anon_client, self.write_client]:
            response = client.get(url)
            self.assertStatusCode(url, response, expected_status=401)

    def test_documents_list(self):
        url = reverse("document-list")
        response = self.read_client.get(url)
        self.assertStatusCode(url, response)
        self.assertEqual(len(response.data), 3)

    def test_documents_list_auth_error(self):
        url = reverse("document-list")
        for client in [self.anon_client, self.write_client]:
            response = client.get(url)
            self.assertStatusCode(url, response, expected_status=401)

    def test_documents_detail(self):
        url = reverse("document-detail", [1])
        response = self.read_client.get(url)
        self.assertStatusCode(url, response)

    def test_documents_detail_auth_error(self):
        url = reverse("document-detail", [1])
        for client in [self.anon_client, self.write_client]:
            response = client.get(url)
            self.assertStatusCode(url, response, expected_status=401)
