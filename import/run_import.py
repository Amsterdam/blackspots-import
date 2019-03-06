import logging
import os
import django
import objectstore

from import_process.fetch_spots import fetch_spots
from import_process.list_documents import get_documents_list

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blackspots_import.settings")
django.setup()

from import_process.clean import clear_models  # noqa
from import_process.import_document_list import import_document_list  # noqa
from import_process.process_xls import process_xls  # noqa

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


STORE_SETTINGS = dict(
    VERSION='2.0',
    AUTHURL='https://identity.stack.cloudvps.com/v2.0',
    TENANT_NAME='BGE000081_WBAkaart',
    TENANT_ID='658fcae781084cc4afa96877caab4804',
    USER=os.getenv('OBJECTSTORE_USER', 'WBAKaart'),
    PASSWORD=os.getenv('BLACKSPOTS_OBJECTSTORE_PASSWORD'),
    REGION_NAME='NL',
)


def perform_import():
    log.info('Clearing models')
    clear_models()

    log.info('Opening object store connection')
    connection = objectstore.get_connection(STORE_SETTINGS)

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




