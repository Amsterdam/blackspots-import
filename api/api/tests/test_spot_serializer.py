from unittest import TestCase, mock

from django.contrib.gis.geos import Point
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from api.serializers import SpotSerializer
from datasets.blackspots.models import Spot


class TestSpotSerializers(TestCase):

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
                             _("jaar_blackspotlijst is required for spot types 'blackspot' and 'wegvak'"))

    def test_jaar_ongeval_quickscan_missing_validation(self):
        for spot_type in [Spot.SpotType.protocol_dodelijk, Spot.SpotType.protocol_ernstig]:
            attrs = {'spot_type': spot_type}
            with self.assertRaises(ValidationError) as context:
                self.serializer.validate(attrs)

            exception_details = context.exception.detail
            self.assertIn('jaar_ongeval_quickscan', exception_details.keys())
            self.assertEqual(str(exception_details['jaar_ongeval_quickscan'][0]),
                             _("jaar_ongeval_quickscan is required for spot types 'protocol_ernstig' "
                             "and 'protocol_dodelijk'"))

    def test_jaar_blackspotlijst_wrong_validation(self):
        for spot_type in [Spot.SpotType.blackspot, Spot.SpotType.wegvak]:
            attrs = {'spot_type': spot_type, 'jaar_ongeval_quickscan': 2019}
            with self.assertRaises(ValidationError) as context:
                self.serializer.validate(attrs)

            exception_details = context.exception.detail
            self.assertIn('jaar_blackspotlijst', exception_details.keys())
            self.assertEqual(str(exception_details['jaar_blackspotlijst'][0]),
                             _("jaar_blackspotlijst is required for spot types 'blackspot' and 'wegvak'"))

    def test_jaar_ongeval_quickscan_wrong_validation(self):
        for spot_type in [Spot.SpotType.protocol_dodelijk, Spot.SpotType.protocol_ernstig]:
            attrs = {'spot_type': spot_type, 'jaar_blackspotlijst': 2019}
            with self.assertRaises(ValidationError) as context:
                self.serializer.validate(attrs)

            exception_details = context.exception.detail
            self.assertIn('jaar_ongeval_quickscan', exception_details.keys())
            self.assertEqual(str(exception_details['jaar_ongeval_quickscan'][0]),
                             _("jaar_ongeval_quickscan is required for spot types 'protocol_ernstig' "
                             "and 'protocol_dodelijk'"))

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
        self.assertEqual(str(exception_details['point'][0]),
                         _('Point is outside Gemeente Amsterdam. To which stadsdeel does the location belong?'))

    @mock.patch('api.serializers.SpotSerializer.determine_stadsdeel')
    def test_coordinate_error(self, determine_stadsdeel):
        determine_stadsdeel.return_value = Spot.Stadsdelen.BagFout

        attrs = {'spot_type': Spot.SpotType.blackspot, 'jaar_blackspotlijst': 2019, 'point': 'test'}
        with self.assertRaises(ValidationError) as context:
            self.serializer.validate(attrs)

        exception_details = context.exception.detail
        self.assertEqual(str(exception_details['point'][0]),
                         _('An error occured finding the stadsdeel. To which stadsdeel does the location belong?'))

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
        # Assert that a ValidationError is raised when 'jaar_blackspotlijst' is missing
        # when spot_type is either blackspot or wegvak (redroute)
        for spot_type in [Spot.SpotType.blackspot, Spot.SpotType.wegvak]:
            attrs = {'spot_type': spot_type}
            with self.assertRaises(ValidationError) as context:
                self.serializer.validate_spot_types(attrs)

        exception_details = context.exception.detail
        self.assertEqual(str(exception_details['jaar_blackspotlijst'][0]),
                         _("jaar_blackspotlijst is required for spot types 'blackspot' and 'wegvak'"))

    def test_validate_spot_types_missing_jaarquickscan(self):
        # Assert that a ValidationError is raised when 'jaar_ongeval_quickscan' is missing
        # when spot_type is protocol_*
        for spot_type in [Spot.SpotType.protocol_ernstig, Spot.SpotType.protocol_dodelijk]:
            attrs = {'spot_type': spot_type}
            with self.assertRaises(ValidationError) as context:
                self.serializer.validate_spot_types(attrs)

        exception_details = context.exception.detail
        self.assertEqual(str(exception_details['jaar_ongeval_quickscan'][0]),
                         _("jaar_ongeval_quickscan is required for spot types "
                           "'protocol_ernstig' and 'protocol_dodelijk'"))

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

    @mock.patch("api.serializers.BagGeoSearchAPI.get_stadsdeel")
    def test_determine_stadsdeel(self, mocked_get_stadsdeel):
        mocked_get_stadsdeel.return_value = 'test'
        result = self.serializer.determine_stadsdeel(Point(x=123, y=789))

        mocked_get_stadsdeel.assert_called_with(lat=789, lon=123)
        self.assertEqual(result, 'test')