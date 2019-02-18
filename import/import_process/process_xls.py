import logging

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


def process_xls(xls_path):
    book = open_workbook(xls_path)

    sheet = book.sheet_by_index(0)

    for row_idx in range(1, sheet.nrows):
        latitude = sheet.cell(row_idx, 2).value
        longitude = sheet.cell(row_idx, 3).value
        try:
            point = Point(latitude, longitude)
        except TypeError as e:
            log_error(f"Unkown point: {latitude}, {longitude}: \"{e}\", skipping")
            continue

        stadsdeel = sheet.cell(row_idx, 4).value
        if len(stadsdeel) != 1:
            log_error(f"Unkown stadsdeel: {stadsdeel}, skipping")
            continue

        spot_data = {
            "spot_id": sheet.cell(row_idx, 0).value,
            "description": sheet.cell(row_idx, 1).value,
            "point": point,
            "stadsdeel": stadsdeel,
            "status": sheet.cell(row_idx, 5).value,
            "jaar_blackspotlijst": get_integer(sheet.cell(row_idx, 14).value, 'blackspotlijst'),
            "jaar_ongeval_quickscan": get_integer(sheet.cell(row_idx, 15).value, 'quickscan'),
            "jaar_oplevering": get_integer(sheet.cell(row_idx, 16).value, 'oplevering'),
        }

        print(spot_data)
        Spot.objects.get_or_create(**spot_data)
