import logging
import os
import django

from objectstore_interaction.connection import get_blackspots_connection
from objectstore_interaction.fetch_spots import fetch_spots
from objectstore_interaction.list_documents import get_documents_list

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blackspots_import.settings")
django.setup()

from import_process.clean import clear_models  # noqa
from import_process.import_document_list import import_document_list  # noqa
from import_process.process_xls import process_xls  # noqa

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def perform_import():
    log.info('Clearing models')
    clear_models()

    log.info('Opening object store connection')
    connection = get_blackspots_connection()

    log.info('Fetching xls file')
    xls = fetch_spots(connection)
    log.info('Importing xls file')
    process_xls(xls)

    log.info('Getting documents list')
    document_list = get_documents_list(connection)
    log.info(f'document list size: {len(document_list)}')

    log.info('Importing document links to model')
    import_document_list(document_list)


if __name__ == "__main__":
    assert os.getenv('BLACKSPOTS_OBJECTSTORE_PASSWORD')
    perform_import()




