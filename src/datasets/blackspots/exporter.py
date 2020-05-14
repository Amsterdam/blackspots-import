from django.db import transaction

from datasets.blackspots.models import Spot, SpotExport


class SpotExporter:

    @staticmethod
    def update_export_table():
        """
        Update the Spots export table
        """
        with transaction.atomic():
            spots = Spot.objects.all().order_by('locatie_id')
            SpotExport.objects.all().delete()
            inserts = []
            for spot in spots:
                inserts.append(SpotExport(
                    locatie_id=spot.locatie_id,
                    spot_type=spot.spot_type,
                    point=spot.point,
                    stadsdeel=spot.stadsdeel,
                    status=spot.status,
                    start_uitvoering=spot.start_uitvoering,
                    eind_uitvoering=spot.eind_uitvoering,
                    jaar_blackspotlijst=spot.jaar_blackspotlijst,
                    jaar_ongeval_quickscan=spot.jaar_ongeval_quickscan,
                    jaar_oplevering=spot.jaar_oplevering,
                ))

            SpotExport.objects.bulk_create(inserts)
