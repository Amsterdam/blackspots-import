import logging

from django.core.management.base import BaseCommand

from datasets.blackspots.exporter import SpotExporter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update Spot export table"

    def handle(self, *args, **options):
        SpotExporter.update_export_table()
