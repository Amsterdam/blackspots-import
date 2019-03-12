import logging
import os
from typing import List, Tuple

from objectstore import get_full_container_list

CONTAINER_NAME = 'doc'
DIR_CONTENT_TYPE = 'application/directory'

DocumentList = List[Tuple[str, str]]

log = logging.getLogger(__name__)


def get_documents_list(connection) -> DocumentList:
    """
    Get list of wba list documents from object store.
    :param connection: swiftclient connection
    :return: Array of documents in the form:
    [('rapportage', 'QE1_rapportage_Some_where - some extra info.pdf'), ... ]
    """
    documents_meta = get_full_container_list(connection, CONTAINER_NAME)
    documents_paths = [
        meta.get('name') for meta in documents_meta if meta.get('content_type') != DIR_CONTENT_TYPE
    ]
    return list(map(os.path.split, documents_paths))
