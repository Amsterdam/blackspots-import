from datapunt_api.rest import HALSerializer
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from datasets.blackspots import models


class DocumentSerializer(HALSerializer):
    spot = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='spot-detail',
        lookup_field='locatie_id',
    )

    class Meta(object):
        model = models.Document
        fields = '__all__'


class SpotDocumentSerializer(HALSerializer):
    id = serializers.ReadOnlyField()

    class Meta(object):
        model = models.Document
        exclude = ['spot']


class SpotGeojsonSerializer(GeoFeatureModelSerializer):
    id = serializers.ReadOnlyField()
    stadsdeel = serializers.CharField(source='get_stadsdeel_display')
    documents = SpotDocumentSerializer(many=True, read_only=True)

    class Meta(object):
        model = models.Spot
        fields = '__all__'
        geo_field = 'point'

        # Detail url is constructed using location_id instead of pk,
        # see: https://www.django-rest-framework.org/api-guide/serializers/#how-hyperlinked-views-are-determined # noqa: 501
        extra_kwargs = {
            '_links': {'lookup_field': 'locatie_id'}
        }


class SpotSerializer(HALSerializer):
    id = serializers.ReadOnlyField()
    stadsdeel = serializers.CharField(source='get_stadsdeel_display')
    documents = SpotDocumentSerializer(many=True, read_only=True)

    class Meta(object):
        model = models.Spot
        fields = '__all__'

        # Detail url is constructed using location_id instead of pk,
        # see: https://www.django-rest-framework.org/api-guide/serializers/#how-hyperlinked-views-are-determined # noqa: 501
        extra_kwargs = {
            '_links': {'lookup_field': 'locatie_id'}
        }
