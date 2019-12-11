from unittest import TestCase

from model_bakery import baker

from api.serializers import SpotCSVSerializer
from datasets.blackspots.models import Spot


class TestSpotSerializers(TestCase):

    def setUp(self):
        self.serializer = SpotCSVSerializer()

    def test_get_jaar(self):
        spot = baker.prepare(Spot, jaar_blackspotlijst=2000, jaar_ongeval_quickscan=2015)

        for spot_type in [Spot.SpotType.blackspot, Spot.SpotType.wegvak]:
            spot.spot_type = spot_type
            self.assertEqual(self.serializer.get_jaar(spot), 2000)

        for spot_type in [Spot.SpotType.protocol_dodelijk, Spot.SpotType.protocol_ernstig]:
            spot.spot_type = spot_type
            self.assertEqual(self.serializer.get_jaar(spot), 2015)

        spot.spot_type = Spot.SpotType.risico
        self.assertEqual(self.serializer.get_jaar(spot), '')
