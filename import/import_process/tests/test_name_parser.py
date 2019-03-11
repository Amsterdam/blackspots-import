from unittest import TestCase

from import_process.name_parser import extract_locatie_id


class TestParser(TestCase):
    def test_extract_locatie_id(self):
        self.assertEqual('B31_2', extract_locatie_id('B31_2_ontwerp_Some street - Other street.pdf'))  # noqa: E501
        self.assertEqual('QSNP123_64', extract_locatie_id('QSNP123_64 _ontwerp_Some street - Other street - extra info.pdf'))  # noqa: E501
        self.assertEqual('B12', extract_locatie_id('B12_rapportage_Some street 2'))  # noqa: E501

    def test_extract_locatie_id_exception(self):
        with self.assertRaises(Exception) as context:
            extract_locatie_id('B_ontwerp_Some street - Other street.pdf')
        self.assertTrue(isinstance(context.exception, ValueError))
        self.assertEqual('Could not find location_id in B_ontwerp_Some street - Other street.pdf', str(context.exception))  # noqa: E501
