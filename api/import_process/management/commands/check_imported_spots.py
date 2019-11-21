import logging

from django.core.management.base import BaseCommand

from datasets.blackspots.models import Document, Spot

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

OBJSTORE_METADATA = 'meta'


class Command(BaseCommand):
    help = 'Import blackspots from objectstore'

    def handle(self, *args, **options):
        log.info("Check import")
        check_import()
        log.info("Check import done")


def assert_count(minimal, actual, message):
    if actual < minimal:
        raise Exception("Import failed. {} minimal {}, actual {}".format(message, minimal, actual))


def check_import():
    log.info('Checking import')
    log.info('Checking database count')

    assert_count(224, Spot.objects.count(), 'Spots count')
    assert_count(164, Document.objects.count(), 'Documents count')

    log.info('Check done')
