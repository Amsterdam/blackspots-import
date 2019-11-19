import logging

import requests
from django.conf import settings

from import_process.util import get_stadsdeel

logger = logging.getLogger(__name__)


class BagGeoSearchAPI:

    FEATURE_STADSDEEL = "gebieden/stadsdeel"

    def get_api_search_url(self, lat, lon):
        return settings.BAG_GEO_SEARCH_API_URL.format(
            lat=lat, lon=lon
        )

    def get_stadsdeel(self, lat, lon):
        url = self.get_api_search_url(lat, lon)

        stadsdeel_code = ''
        try:
            response = requests.get(url)
            content = response.json()
            features = content.get('features', [])
            for feature in features:
                properties = feature.get('properties', {})
                if properties.get('type') == BagGeoSearchAPI.FEATURE_STADSDEEL:
                    stadsdeel_code = properties.get('code')
                    break
        except:
            logger.exception("Failed to get stadsdeel from lat/lon")

        return get_stadsdeel(stadsdeel_code)
