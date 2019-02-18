import logging
import os
import django
from import_process.fetch_spots import fetch_spots

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blackspots_import.settings")
django.setup()

from import_process.process_xls import process_xls

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


if __name__ == "__main__":
    assert os.getenv('BLACKSPOTS_OBJECTSTORE_PASSWORD')
    xls = fetch_spots()
    process_xls(xls)



