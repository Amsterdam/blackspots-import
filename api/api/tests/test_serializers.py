from unittest import TestCase

from rest_framework.exceptions import ValidationError

from api.serializers import SpotSerializer
from datasets.blackspots.models import Spot


class TestSerializers(TestCase):

    def setUp(self):
        self.serializer = SpotSerializer()

    def test_jaar_blackspotlijst_missing_validation(self):
        for spot_type in [Spot.SpotType.blackspot, Spot.SpotType.wegvak]:
            attrs = {'spot_type': spot_type}
            with self.assertRaises(ValidationError) as context:
                self.serializer.validate(attrs)

            exception_details = context.exception.detail
            self.assertIn('jaar_blackspotlijst', exception_details.keys())
            self.assertEqual(str(exception_details['jaar_blackspotlijst'][0]),
                             "jaar_blackspotlijst is required for spot types 'blackspot' and 'wegvak'")

    def test_jaar_ongeval_quickscan_missing_validation(self):
        for spot_type in [Spot.SpotType.protocol_dodelijk, Spot.SpotType.protocol_ernstig]:
            attrs = {'spot_type': spot_type}
            with self.assertRaises(ValidationError) as context:
                self.serializer.validate(attrs)

            exception_details = context.exception.detail
            self.assertIn('jaar_ongeval_quickscan', exception_details.keys())
            self.assertEqual(str(exception_details['jaar_ongeval_quickscan'][0]),
                             "jaar_ongeval_quickscan is required for spot types 'protocol_ernstig' "
                             "and 'protocol_dodelijk'")

    def test_jaar_blackspotlijst_wrong_validation(self):
        for spot_type in [Spot.SpotType.blackspot, Spot.SpotType.wegvak]:
            attrs = {'spot_type': spot_type, 'jaar_ongeval_quickscan': 2019}
            with self.assertRaises(ValidationError) as context:
                self.serializer.validate(attrs)

            exception_details = context.exception.detail
            self.assertIn('jaar_blackspotlijst', exception_details.keys())
            self.assertEqual(str(exception_details['jaar_blackspotlijst'][0]),
                             "jaar_blackspotlijst is required for spot types 'blackspot' and 'wegvak'")

    def test_jaar_ongeval_quickscan_wrong_validation(self):
        for spot_type in [Spot.SpotType.protocol_dodelijk, Spot.SpotType.protocol_ernstig]:
            attrs = {'spot_type': spot_type, 'jaar_blackspotlijst': 2019}
            with self.assertRaises(ValidationError) as context:
                self.serializer.validate(attrs)

            exception_details = context.exception.detail
            self.assertIn('jaar_ongeval_quickscan', exception_details.keys())
            self.assertEqual(str(exception_details['jaar_ongeval_quickscan'][0]),
                             "jaar_ongeval_quickscan is required for spot types 'protocol_ernstig' "
                             "and 'protocol_dodelijk'")

    def test_jaar_blackspotlijst_validation_success(self):
        for spot_type in [Spot.SpotType.blackspot, Spot.SpotType.wegvak]:
            attrs = {'spot_type': spot_type, 'jaar_blackspotlijst': 2019}
            self.serializer.validate(attrs)
            # no errors expected

    def test_jaar_ongeval_quickscan_validation_success(self):
        for spot_type in [Spot.SpotType.protocol_ernstig, Spot.SpotType.protocol_dodelijk]:
            attrs = {'spot_type': spot_type, 'jaar_ongeval_quickscan': 2019}
            self.serializer.validate(attrs)
            # no errors expected
