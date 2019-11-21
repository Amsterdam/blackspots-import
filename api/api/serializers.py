from datapunt_api.rest import HALSerializer
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from api.bag_geosearch import BagGeoSearchAPI
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
    stadsdeel = serializers.CharField(source='get_stadsdeel_display', read_only=True)
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
    stadsdeel = serializers.CharField(source='get_stadsdeel_display', read_only=True)
    documents = SpotDocumentSerializer(many=True, read_only=True)
    rapport_document = serializers.FileField(use_url=True, required=False)
    design_document = serializers.FileField(use_url=True, required=False)

    def create(self, validated_data):
        # before creating the spot, we'll need to obtain the 'stadsdeel' based on the
        # Point value.

        point = validated_data.get('point')
        lat = point.y
        lon = point.x
        stadsdeel = BagGeoSearchAPI().get_stadsdeel(lat, lon)
        validated_data['stadsdeel'] = stadsdeel

        if 'rapport_document' in validated_data:
            # TODO: do something with the document
            del validated_data['rapport_document']

        if 'design_document' in validated_data:
            # TODO: do something with the document
            del validated_data['design_document']

        spot = super().create(validated_data)

        return spot

    class Meta(object):
        model = models.Spot
        fields = '__all__'

        # Detail url is constructed using location_id instead of pk,
        # see: https://www.django-rest-framework.org/api-guide/serializers/#how-hyperlinked-views-are-determined # noqa: 501
        extra_kwargs = {
            '_links': {'lookup_field': 'locatie_id'}
        }
