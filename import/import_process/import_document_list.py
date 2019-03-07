import logging

from datasets.blackspots.models import Spot, Document
from objectstore_interaction.list_documents import DocumentList
from import_process.name_parser import extract_locatie_id

log = logging.getLogger(__name__)


document_type_mapping = {
    'ontwerp': Document.DOCUMENT_TYPE[0][0],
    'rapportage': Document.DOCUMENT_TYPE[1][0]
}


def create_document(type_str: str, filename: str, spot: Spot) -> Document:
    try:
        document_type = document_type_mapping.get(type_str)
    except ValueError as e:
        log.error(f'Did not recognize document type: {type_str}, skipping, {e}')
        return
    return Document.objects.create(type=document_type, filename=filename, spot=spot)


def import_document_list(document_list: DocumentList):
    """
    Create document models and link them to the related Spots
    """

    for (type_str, filename) in document_list:
        locatie_id = extract_locatie_id(filename)

        try:
            spot = Spot.objects.get(locatie_id=locatie_id)
        except Spot.DoesNotExist:
            log.error(f'could find spot for locatie_id: {locatie_id}, document filename: {filename}, skipping')
            continue

        create_document(type_str, filename, spot)

    log.info(f'Document count: {Document.objects.all().count()}')
