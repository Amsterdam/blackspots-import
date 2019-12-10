from unittest import TestCase, mock

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

    @mock.patch('api.serializers.SpotSerializer.determine_stadsdeel')
    def test_coordinate_outside_amsterdam(self, determine_stadsdeel):
        determine_stadsdeel.return_value = Spot.Stadsdelen.Geen

        attrs = {'spot_type': Spot.SpotType.blackspot, 'jaar_blackspotlijst': 2019, 'point': 'test'}
        with self.assertRaises(ValidationError) as context:
            self.serializer.validate(attrs)

        exception_details = context.exception.detail
        self.assertEqual(str(exception_details['point'][0]), 'Point could not be matched to stadsdeel')

    @mock.patch('api.serializers.SpotSerializer.determine_stadsdeel')
    def test_coordinate_error(self, determine_stadsdeel):
        determine_stadsdeel.return_value = Spot.Stadsdelen.BagFout

        attrs = {'spot_type': Spot.SpotType.blackspot, 'jaar_blackspotlijst': 2019, 'point': 'test'}
        with self.assertRaises(ValidationError) as context:
            self.serializer.validate(attrs)

        exception_details = context.exception.detail
        self.assertEqual(str(exception_details['point'][0]), 'Failed to get stadsdeel for point')

    def test_jaar_blackspotlijst_none(self):
        # Assert that the jaar_blackspotlijst property is changed to None
        for spot_type in [Spot.SpotType.protocol_ernstig, Spot.SpotType.protocol_dodelijk]:
            attrs = {'spot_type': spot_type, 'jaar_ongeval_quickscan': 2019, 'jaar_blackspotlijst': 2020}
            self.serializer.validate(attrs)
            self.assertIn('jaar_blackspotlijst', attrs)
            self.assertEqual(attrs['jaar_blackspotlijst'], None)

    def test_jaar_ongeval_quickscan_none(self):
        # Assert that the jaar_ongeval_quickscan property is changed to None
        for spot_type in [Spot.SpotType.blackspot, Spot.SpotType.wegvak]:
            attrs = {'spot_type': spot_type, 'jaar_blackspotlijst': 2019, 'jaar_ongeval_quickscan': 2020}
            self.serializer.validate(attrs)
            self.assertIn('jaar_ongeval_quickscan', attrs)
            self.assertEqual(attrs['jaar_ongeval_quickscan'], None)

    def test_jaar_blackspotlijst_missing_none(self):
        # Assert that the jaar_blackspotlijst property is added and set to None
        for spot_type in [Spot.SpotType.protocol_ernstig, Spot.SpotType.protocol_dodelijk]:
            attrs = {'spot_type': spot_type, 'jaar_ongeval_quickscan': 2019}
            self.serializer.validate(attrs)
            self.assertIn('jaar_blackspotlijst', attrs)
            self.assertEqual(attrs['jaar_blackspotlijst'], None)

    def test_jaar_ongeval_quickscan_missing_none(self):
        # Assert that the jaar_ongeval_quickscan property is added and set to None
        for spot_type in [Spot.SpotType.blackspot, Spot.SpotType.wegvak]:
            attrs = {'spot_type': spot_type, 'jaar_blackspotlijst': 2019}
            self.serializer.validate(attrs)
            self.assertIn('jaar_ongeval_quickscan', attrs)
            self.assertEqual(attrs['jaar_ongeval_quickscan'], None)

    def test_validate_spot_types_missing_jaarblackspotlijst(self):
        for spot_type in [Spot.SpotType.blackspot, Spot.SpotType.wegvak]:
            attrs = {'spot_type': spot_type}
            with self.assertRaises(ValidationError):
                self.serializer.validate_spot_types(attrs)

    def test_validate_spot_types_missing_jaarquickscan(self):
        for spot_type in [Spot.SpotType.protocol_ernstig, Spot.SpotType.protocol_dodelijk]:
            attrs = {'spot_type': spot_type}
            with self.assertRaises(ValidationError):
                self.serializer.validate_spot_types(attrs)

    def test_validate_spot_types_unset_jaarquickscan(self):
        for spot_type in [Spot.SpotType.blackspot, Spot.SpotType.wegvak]:
            attrs = {'spot_type': spot_type, 'jaar_blackspotlijst': 2019}
            self.serializer.validate_spot_types(attrs)
            self.assertEqual(attrs['jaar_ongeval_quickscan'], None)

    def test_validate_spot_types_unset_jaarblackspotlijst(self):
        for spot_type in [Spot.SpotType.protocol_ernstig, Spot.SpotType.protocol_dodelijk]:
            attrs = {'spot_type': spot_type, 'jaar_ongeval_quickscan': 2019}
            self.serializer.validate_spot_types(attrs)
            self.assertEqual(attrs['jaar_blackspotlijst'], None)

    def test_validate_spot_types_unset_both(self):
        for spot_type in [Spot.SpotType.risico]:
            attrs = {'spot_type': spot_type}
            self.serializer.validate_spot_types(attrs)
            self.assertEqual(attrs['jaar_blackspotlijst'], None)
            self.assertEqual(attrs['jaar_ongeval_quickscan'], None)
