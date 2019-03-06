from api import serializers

from datapunt_api.rest import DatapuntViewSet

from datasets.blackspots import models


class SpotViewSet(DatapuntViewSet):
    queryset = models.Spot.objects.all().order_by('pk')
    serializer_class = serializers.SpotSerializer
    serializer_detail_class = serializers.SpotSerializer
    lookup_field = 'locatie_id'


class DocumentViewSet(DatapuntViewSet):
    queryset = models.Document.objects.all().order_by('pk')
    serializer_class = serializers.DocumentSerializer
    serializer_detail_class = serializers.DocumentSerializer
