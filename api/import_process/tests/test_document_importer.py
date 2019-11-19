from unittest import skip

from django.test import TestCase
from model_mommy import mommy

from datasets.blackspots.models import Document, Spot
from import_process.process_xls import InputError, create_document


class TestDocumentImporter(TestCase):

    def setUp(self):
        self.spot = mommy.make(Spot)

    def test_correct_reference(self):
        filename = 'foo_bar with spaces.pdf'
        available_documents = [
            ('rapportage', filename,),
        ]

        create_document(available_documents, Document.DocumentType.Rapportage, filename, self.spot)

        document = Document.objects.get()
        self.assertEqual(document.filename, filename)
        self.assertEqual(document.type, Document.DocumentType.Rapportage)
        self.assertEqual(document.spot, self.spot)

    @skip  # TODO activate when import is throwing exception
    def test_unavailable_reference(self):
        filename = 'foo_bar with spaces.pdf'
        available_documents = [
            ('rapportage', filename,),
        ]

        self.assertRaises(
            InputError,
            create_document,

            available_documents,
            Document.DocumentType.Rapportage,
            'other file name.pdf',
            self.spot
        )

        self.assertEqual(Document.objects.count(), 0)
