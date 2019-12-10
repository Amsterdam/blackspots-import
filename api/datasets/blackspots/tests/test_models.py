from unittest import TestCase, mock

from model_bakery import baker

from datasets.blackspots.models import Document, Spot


class TestSpot(TestCase):
    def test_str(self):
        spot = baker.prepare(Spot, locatie_id='abcdef', spot_type=Spot.SpotType.blackspot)
        self.assertEqual(str(spot), 'abcdef: blackspot')


class TestDocument(TestCase):

    @mock.patch('datasets.blackspots.models.Document._generate_filename')
    @mock.patch('django.contrib.gis.db.models.Model.save')
    def test_save_without_filename(self, mocked_save, mocked_name_generator):
        """
        Test and assert that saving a Document without a filename
        will set its filename before saving the instance to the database.
        """
        mocked_save.return_value = None
        mocked_name_generator.return_value = "filename.txt"
        spot = baker.prepare(Spot)
        document = baker.prepare(Document, spot=spot, filename=None)
        document.save()
        mocked_name_generator.assert_called()
        self.assertEqual(document.filename, 'filename.txt')

    @mock.patch('datasets.blackspots.models.Document._generate_filename')
    @mock.patch('django.contrib.gis.db.models.Model.save')
    def test_save_with_filename(self, mocked_save, mocked_name_generator):
        """
        Test and assert that saving a Document with a filename will
        not override its existing filename.
        """
        mocked_save.return_value = None
        spot = baker.prepare(Spot)
        document = baker.prepare(Document, spot=spot, filename='doc_filename.txt')
        document.save()
        mocked_name_generator.assert_not_called()
        self.assertEqual(document.filename, 'doc_filename.txt')

    def test_generate_filename(self):
        """
        Test and assert that the correct filename is generated for a Document and
        its corresponding Spot. Note that the filename will be 'slugified', and
        therefore 'test desc' will become 'test_desc', and everything will be
        lowercase.
        """
        spot = baker.prepare(Spot, locatie_id='EFGHIJ', description='test desc')
        document = baker.prepare(Document, type=Document.DocumentType.Ontwerp, spot=spot)
        self.assertEqual(document._generate_filename(), 'efghij_ontwerp_test-desc.pdf')

    def test_generate_filename_exception(self):
        """
        Test and assert that an exception is raised when we try to generate the
        filename for a document that has no Spot. The Spot is needed because
        its location_id and description will be part of the filename.
        """
        document = baker.prepare(Document, type=Document.DocumentType.Ontwerp, spot=None)
        with self.assertRaises(Exception, msg='Spot must be set'):
            document._generate_filename()
