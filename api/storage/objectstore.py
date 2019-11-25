import logging
import os
from typing import List, Tuple

from objectstore import get_full_container_list, objectstore

CONTAINER_NAME = 'doc'
from datasets.blackspots.models import Document

DIR_CONTENT_TYPE = 'application/directory'

XLS_OBJECT_NAME = 'VVP_Blackspot_Voortgangslijst_Kaart_actueel.xls'
DOWNLOAD_DIR = '/tmp/blackspots/'
WBA_CONTAINER_NAME = 'wbalijst'

DocumentList = List[Tuple[str, str]]


class ObjectStore:

    logger = logging.getLogger(__name__)

    def __init__(self, config):
        self.config = config
        super().__init__()

    def get_connection(self):
        connection = objectstore.get_connection(self.config)
        return connection

    def upload(self, file, document: Document):
        self.logger.info(f"Uploading {file} to objectstore: {document.filename}")
        connection = self.get_connection()
        connection.put_object(CONTAINER_NAME, document.filename, file)
        self.logger.info("Done uploading to objectstore")

    def get_document(self, connection, container_name: str, object_name: str):
        self.logger.debug(f'Fetching file from objectstore: {container_name}, {object_name}')
        return connection.get_object(container_name, object_name)

    def get_wba_documents_list(self, connection) -> DocumentList:
        """
        Get list of wba list documents from object store.
        :param connection: swiftclient connection
        :return: Array of documents in the form:
        [('rapportage', 'QE1_rapportage_Some_where - some extra info.pdf'), ... ]
        """
        documents_meta = get_full_container_list(connection, WBA_CONTAINER_NAME)
        documents_paths = [
            meta.get('name') for meta in documents_meta if
            meta.get('content_type') != DIR_CONTENT_TYPE
        ]
        return list(map(os.path.split, documents_paths))

    def get_file(self, connection, container_name, object_name):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        output_path = os.path.join(DOWNLOAD_DIR, object_name)

        if os.path.isfile(output_path):
            self.logger.info(f"Using cached file: {object_name}")
        else:
            self.logger.info(f"Fetching file: {object_name}")
            new_data = connection.get_object(container_name, object_name)[1]
            with open(output_path, 'wb') as file:
                file.write(new_data)
        return output_path

    def fetch_spots(self, connection):
        return self.get_file(connection, CONTAINER_NAME, XLS_OBJECT_NAME)
