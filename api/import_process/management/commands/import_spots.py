import logging
import os

from django.core.management.base import BaseCommand

from datasets.blackspots.models import Document, Spot
from import_process.clean import clear_models
from import_process.process_xls import process_xls
from objectstore_interaction.connection import get_blackspots_connection
from objectstore_interaction.fetch_spots import fetch_spots
from objectstore_interaction.list_documents import get_documents_list

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import blackspots from objectstore'

    def handle(self, *args, **options):
        assert os.getenv('BLACKSPOTS_OBJECTSTORE_PASSWORD')
        perform_import()


def perform_import():
    log.info('Clearing models')
    clear_models()

    log.info('Opening object store connection')
    connection = get_blackspots_connection()

    log.info('Getting documents list')
    document_list = get_documents_list(connection)
    log.info(f'document list size: {len(document_list)}')

    log.info('Fetching xls file')
    xls_path = fetch_spots(connection)
    log.info('Importing xls file')
    process_xls(xls_path, document_list)

    log.info(f'Spot count: {Spot.objects.all().count()}')
    log.info(f'Document count: {Document.objects.all().count()}')
