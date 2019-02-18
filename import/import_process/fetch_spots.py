import logging
import os

import objectstore

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


DOWNLOAD_DIR = '/tmp/blackspots/'


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


def fetch_spots():
    connection = objectstore.get_connection(STORE_SETTINGS)

    return get_file(connection, 'wbalijst', 'VVP_Blackspot_Voortgangslijst_Kaart_actueel.xls')


