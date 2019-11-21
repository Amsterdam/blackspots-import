from django.core.management.base import BaseCommand

from api.bag_geosearch import BagGeoSearchAPI
from datasets.blackspots.models import Spot


class Command(BaseCommand):
    help = 'Try to determine the stadsdeel for each Spot where stadsdeel ' \
           'is unknown due to earlier connection errors'

    def handle(self, *args, **options):
        spots = Spot.objects.filter(stadsdeel=Spot.Stadsdelen.BagFout)
        bag_geosearch_api = BagGeoSearchAPI()
        for spot in spots:
            lat = spot.point.y
            lon = spot.point.x
            stadsdeel = bag_geosearch_api.get_stadsdeel(lat=lat, lon=lon)
            if stadsdeel != spot.stadsdeel:
                spot.stadsdeel = stadsdeel
                spot.save()
