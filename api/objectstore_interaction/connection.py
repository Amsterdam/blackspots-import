import os

from objectstore import objectstore


STORE_SETTINGS = dict(
    VERSION='2.0',
    AUTHURL='https://identity.stack.cloudvps.com/v2.0',
    TENANT_NAME='BGE000081_WBAkaart',
    TENANT_ID='658fcae781084cc4afa96877caab4804',
    USER=os.getenv('OBJECTSTORE_USER', 'WBAKaart'),
    PASSWORD=os.getenv('BLACKSPOTS_OBJECTSTORE_PASSWORD'),
    REGION_NAME='NL',
)


def get_blackspots_connection():
    assert os.getenv('BLACKSPOTS_OBJECTSTORE_PASSWORD')
    connection = objectstore.get_connection(STORE_SETTINGS)
    return connection
