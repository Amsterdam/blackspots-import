import logging
import os

XLS_OBJECT_NAME = 'VVP_Blackspot_Voortgangslijst_Kaart_actueel.xls'
DOWNLOAD_DIR = '/tmp/blackspots/'
CONTAINER_NAME = 'wbalijst'

log = logging.getLogger(__name__)


def get_file(connection, container_name, object_name):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    output_path = os.path.join(DOWNLOAD_DIR, object_name)

    if os.path.isfile(output_path):
        log.info(f"Using cached file: {object_name}")
    else:
        log.info(f"Fetching file: {object_name}")
        new_data = connection.get_object(container_name, object_name)[1]
        with open(output_path, 'wb') as file:
            file.write(new_data)
    return output_path


def fetch_spots(connection):
    return get_file(connection, CONTAINER_NAME, XLS_OBJECT_NAME)
