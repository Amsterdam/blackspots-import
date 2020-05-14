import logging

import requests
from django.conf import settings
from requests import RequestException

from datasets.blackspots.models import Spot
from import_process.util import get_stadsdeel

logger = logging.getLogger(__name__)


class BagGeoSearchAPI:

    FEATURE_STADSDEEL = "gebieden/stadsdeel"

    def get_stadsdeel(self, lat, lon):
        url = settings.BAG_GEO_SEARCH_API_URL

        try:
            response = requests.get(url, params={'lon': lon, 'lat': lat})
            response.raise_for_status()
            content = response.json()
            features = content.get('features', [])
            for feature in features:
                properties = feature.get('properties', {})
                if properties.get('type') == BagGeoSearchAPI.FEATURE_STADSDEEL:
                    stadsdeel_code = properties.get('code')
                    return get_stadsdeel(stadsdeel_code)
        except (RequestException, ValueError):
            logger.exception("Failed to get stadsdeel from lat/lon")
            return Spot.Stadsdelen.BagFout

        return Spot.Stadsdelen.Geen
