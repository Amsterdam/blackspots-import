import logging


log = logging.getLogger(__name__)


def get_actual_document(connection, container_name: str, object_name: str):
    log.debug(f'Fetching file from objectstore: {container_name}, {object_name}')

    store_object = connection.get_object(container_name, object_name)

    return store_object
