import logging

from django.core.management.base import BaseCommand

from api.bag_geosearch import BagGeoSearchAPI
from datasets.blackspots.models import Spot


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Try to determine the stadsdeel for each Spot where stadsdeel ' \
           'is unknown due to earlier connection errors'

    def handle(self, *args, **options):
        spots = Spot.objects.filter(stadsdeel=Spot.Stadsdelen.BagFout)
        bag_geosearch_api = BagGeoSearchAPI()
        update_dict = {}
        for spot in spots:
            lat = spot.point.y
            lon = spot.point.x
            stadsdeel = bag_geosearch_api.get_stadsdeel(lat=lat, lon=lon)
            if stadsdeel != spot.stadsdeel:
                spot.stadsdeel = stadsdeel
                spot.save()

            if stadsdeel not in update_dict:
                update_dict[stadsdeel] = 1
            else:
                update_dict[stadsdeel] += 1

        for stadsdeel in update_dict:
            logger.info(f"Updated {update_dict[stadsdeel]} Spots to {stadsdeel}")
        else:
            logger.info("No Spots updated; all have correct stadsdeel")
