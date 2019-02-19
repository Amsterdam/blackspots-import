from datapunt_api.rest import HALSerializer

from datasets.blackspots import models


class SpotSerializer(HALSerializer):
    class Meta(object):
        model = models.Spot
        fields = '__all__'

