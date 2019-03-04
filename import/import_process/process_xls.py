import logging
import random

from django.contrib.gis.geos import Point
from xlrd import open_workbook

from datasets.blackspots.models import Spot


log = logging.getLogger(__name__)


def log_error(message):
    log.error(message)


def get_integer(field, field_name):
    try:
        return int(field)
    except ValueError as e:
        log_error(f"Error parsing {field}, {field_name}: '{e}'")
        return None


def get_spot_type(jaar_blackspotslijst, jaar_quickscan):
    if jaar_blackspotslijst:
        return 'Blackspot'
    if jaar_quickscan:
        if random.choice([True, False]):
            return 'Protocol_ernstig'
        else:
            return 'Protocol_dodelijk'
    return random.choice(['Risico', 'Wegvak'])


def process_xls(xls_path):
    book = open_workbook(xls_path)

    sheet = book.sheet_by_index(0)

    for row_idx in range(1, sheet.nrows):
        latitude = sheet.cell(row_idx, 2).value
        longitude = sheet.cell(row_idx, 3).value
        try:
            point = Point(longitude, latitude)
        except TypeError as e:
            log_error(f"Unkown point: {latitude}, {longitude}: \"{e}\", skipping")
            continue

        stadsdeel = sheet.cell(row_idx, 4).value
        if len(stadsdeel) != 1:
            log_error(f"Unkown stadsdeel: {stadsdeel}, skipping")
            continue

        jaar_blackspotlijst = get_integer(sheet.cell(row_idx, 14).value, 'blackspotlijst')
        jaar_quickscan = get_integer(sheet.cell(row_idx, 15).value, 'quickscan')
        spot_type = get_spot_type(jaar_blackspotlijst, jaar_quickscan)
        spot_data = {
            "spot_id": sheet.cell(row_idx, 0).value,
            "spot_type": spot_type,
            "description": sheet.cell(row_idx, 1).value,
            "point": point,
            "stadsdeel": stadsdeel,
            "status": sheet.cell(row_idx, 5).value,
            "jaar_blackspotlijst": jaar_blackspotlijst,
            "jaar_ongeval_quickscan": jaar_quickscan,
            "jaar_oplevering": get_integer(sheet.cell(row_idx, 16).value, 'oplevering'),
        }

        print(spot_data)
        Spot.objects.get_or_create(**spot_data)
