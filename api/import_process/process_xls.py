import logging

from django.contrib.gis.geos import Point
from xlrd import open_workbook

from datasets.blackspots.models import Spot, Document
from objectstore_interaction.list_documents import DocumentList

log = logging.getLogger(__name__)

EXCEL_STRUCTURE = {
    'number':               {'column_idx': 0, 'header': 'Nummer'},
    'description':          {'column_idx': 1, 'header': 'Locatie omschrijving'},
    'type':                 {'column_idx': 2, 'header': 'Type'},
    'lat':                  {'column_idx': 3, 'header': 'Lat'},
    'lng':                  {'column_idx': 4, 'header': 'Long'},
    'stadsdeel':            {'column_idx': 5, 'header': 'Stadsdeel'},
    'status':               {'column_idx': 6, 'header': 'Status'},
    'actiehouders':         {'column_idx': 7, 'header': 'Actiehouders'},
    'tasks':                {'column_idx': 8, 'header': 'Taken'},
    'start_uitvoering':     {'column_idx': 9, 'header': 'Start uitvoering'},
    'eind_uitvoering':      {'column_idx': 10, 'header': 'Eind uitvoering'},
    'jaar_blackspot':       {'column_idx': 11, 'header': 'Jaar Blackspotlijst'},
    'jaar_quickscan':       {'column_idx': 12, 'header': 'Jaar ongeval quickscan rapportage'},
    'jaar_oplevering':      {'column_idx': 13, 'header': 'Jaar oplevering'},
    'opmerkingen':          {'column_idx': 14, 'header': 'Opmerkingen'},
    'rapportage':           {'column_idx': 15, 'header': 'Rapportage'},
    'ontwerp':              {'column_idx': 16, 'header': 'Verkeersontwerp'},
}


def get_sheet_cell(sheet, column_name, row_idx):
    value = EXCEL_STRUCTURE.get(column_name)
    assert value is not None, f'column name not recognised: {column_name}'
    return sheet.cell(row_idx, value.get('column_idx')).value


def assert_column_name(sheet, column_idx, expected):
    value = sheet.cell(0, column_idx).value.strip()
    assert value == expected, f'header {column_idx} is not expected value {expected} but {value}'


def check_column_names(sheet):
    for value in EXCEL_STRUCTURE.values():
        if value.get('skip', False):
            continue
        assert_column_name(sheet, value.get('column_idx'), value.get('header'))


class InputError(Exception):
    pass


def log_error(message):
    log.error(message)


def get_integer(value, field_name):
    if value is None or value == '':
        return None
    try:
        return int(value)
    except ValueError as e:
        log_error(f"Error parsing {value}, {field_name}: '{e}'")
        return None


def get_spot_type(abbreviation):
    excel_to_enum = {
        'B': Spot.SpotType.blackspot,
        'BW': Spot.SpotType.wegvak,
        'QD': Spot.SpotType.protocol_dodelijk,
        'QE': Spot.SpotType.protocol_ernstig,
        # Note, intentionally mapping protocol to Risk type. No risk type is available a.t.m.
        'QSNP': Spot.SpotType.risico,
        'R': Spot.SpotType.risico,
    }
    value = excel_to_enum.get(abbreviation.strip())
    if not value:
        raise InputError(f'Unkown type value: {abbreviation}')
    else:
        return value


def get_status(name: str):
    excel_to_enum = {
        'Onbekend': Spot.StatusChoice.onbekend,
        'Gereed': Spot.StatusChoice.gereed,
        'Voorbereiding': Spot.StatusChoice.voorbereiding,
        'Onderzoek/ontwerp': Spot.StatusChoice.onderzoek_ontwerp,
        'Uitvoering': Spot.StatusChoice.uitvoering,
        'Geen maatregel': Spot.StatusChoice.geen_maatregel,
    }
    value = excel_to_enum.get(name.strip())
    if not value:
        raise InputError(f'Unkown status value: {name}')
    else:
        return value


def get_stadsdeel(name: str):
    excel_to_enum = {
        'T': Spot.Stadsdelen.Zuidoost,
        'A': Spot.Stadsdelen.Centrum,
        'N': Spot.Stadsdelen.Noord,
        'B': Spot.Stadsdelen.Westpoort,
        'E': Spot.Stadsdelen.West,
        'F': Spot.Stadsdelen.Nieuw_West,
        'K': Spot.Stadsdelen.Zuid,
        'M': Spot.Stadsdelen.Oost,
        'Geen': Spot.Stadsdelen.Geen,
    }
    value = excel_to_enum.get(name.strip())
    if not value:
        raise InputError(f"Unkown stadsdeel: {name}, skipping")
    return value


def create_document(
        document_list: DocumentList,
        doc_type: Document.DocumentType,
        filename: str,
        spot: Spot
    ):
    if not filename or len(filename) == 0:
        return

    available_filenames = [filename for [_, filename] in document_list]
    if filename not in available_filenames:
        log_error(f'Missing file on object store: {filename} of type {doc_type}')
        return

    Document.objects.create(type=doc_type, filename=filename, spot=spot)


def process_xls(xls_path, document_list: DocumentList):
    book = open_workbook(xls_path)

    sheet = book.sheet_by_index(0)

    check_column_names(sheet)

    for row_idx in range(1, sheet.nrows):
        latitude = get_sheet_cell(sheet, 'lat', row_idx)
        longitude = get_sheet_cell(sheet, 'lng', row_idx)
        try:
            point = Point(longitude, latitude)
        except TypeError as e:
            # TODO raise exception
            log_error(f"Unknown point: {latitude}, {longitude}: \"{e}\", skipping")
            continue

        stadsdeel = get_stadsdeel(get_sheet_cell(sheet, 'stadsdeel', row_idx))

        jaar_blackspotlijst = get_integer(get_sheet_cell(sheet, 'jaar_blackspot', row_idx), 'blackspotlijst')
        jaar_quickscan = get_integer(get_sheet_cell(sheet, 'jaar_quickscan', row_idx), 'quickscan')
        spot_type = get_spot_type(get_sheet_cell(sheet, 'type', row_idx))
        spot_data = {
            "locatie_id": get_sheet_cell(sheet, 'number', row_idx),
            "actiehouders": get_sheet_cell(sheet, 'actiehouders', row_idx),
            "spot_type": spot_type,
            "description": get_sheet_cell(sheet, 'description', row_idx),
            "point": point,
            "stadsdeel": stadsdeel,
            "status": get_status(get_sheet_cell(sheet, 'status', row_idx)),
            "jaar_blackspotlijst": jaar_blackspotlijst,
            "jaar_ongeval_quickscan": jaar_quickscan,
            "jaar_oplevering": get_integer(get_sheet_cell(sheet, 'jaar_oplevering', row_idx), 'oplevering'),
        }

        [spot, _] = Spot.objects.get_or_create(**spot_data)

        create_document(document_list, Document.DocumentType.Rapportage, get_sheet_cell(sheet, 'rapportage', row_idx), spot)
        create_document(document_list, Document.DocumentType.Ontwerp, get_sheet_cell(sheet, 'ontwerp', row_idx), spot)
