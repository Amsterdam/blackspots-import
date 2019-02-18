import logging
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blackspots_import.settings")
django.setup()

from datasets.blackspots import models

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

OBJSTORE_METADATA = 'meta'


def assert_count(minimal, actual, message):
    if actual < minimal:
        raise Exception("Import failed. {} minimal {}, actual {}".format(message, minimal, actual))


def check_import():
    log.info('Checking import')
    log.info('Checking database count')

    assert_count(200, models.Spot.objects.count(), 'Tellus count')

    log.info('Check done')


if __name__ == "__main__":
    log.info("Check import")
    check_import()
    log.info("Check import done")
