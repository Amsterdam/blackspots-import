from unittest import TestCase

from api.serializers import DisplayChoiceField


class DisplayChoiceFieldTestCase(TestCase):

    def setUp(self) -> None:
        self.choice_field = DisplayChoiceField(choices=[('a', '1'), ('b', '2')])

    def test_to_representation(self):
        self.assertEqual(self.choice_field.to_representation('a'), '1')

    def test_to_representation_empty(self):
        self.assertEqual(self.choice_field.to_representation(''), '')

    def test_to_representation_none(self):
        self.assertEqual(self.choice_field.to_representation(None), None)
