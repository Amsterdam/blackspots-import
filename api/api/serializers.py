from datapunt_api.rest import HALSerializer
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from api.bag_geosearch import BagGeoSearchAPI
from datasets.blackspots import models
from datasets.blackspots.models import Document, Spot


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

    def validate_stadsdeel(self, value):
        if value == Spot.Stadsdelen.Geen:
            raise serializers.ValidationError('Coordinate could not be matched to stadsdeel')
        elif value == Spot.Stadsdelen.BagFout:
            raise serializers.ValidationError('Failed to get stadsdeel for coordinate')
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        spot_type = attrs.get('spot_type')
        if spot_type in [Spot.SpotType.blackspot, Spot.SpotType.wegvak]:
            if not attrs.get('jaar_blackspotlijst'):
                raise serializers.ValidationError({
                    'jaar_blackspotlijst': [
                        "jaar_blackspotlijst is required for spot types 'blackspot' and 'wegvak'"
                    ]
                })

        elif spot_type in [Spot.SpotType.protocol_ernstig, Spot.SpotType.protocol_dodelijk]:
            if not attrs.get('jaar_ongeval_quickscan'):
                raise serializers.ValidationError({
                    'jaar_ongeval_quickscan': [
                        "jaar_ongeval_quickscan is required for spot types 'protocol_ernstig' and 'protocol_dodelijk'"
                    ]
                })

        return attrs

    def create(self, validated_data):
        # before creating the spot, we'll need to obtain the 'stadsdeel' based on the
        # Point value.

        point = validated_data.get('point')
        lat = point.y
        lon = point.x
        stadsdeel = BagGeoSearchAPI().get_stadsdeel(lat, lon)
        validated_data['stadsdeel'] = stadsdeel

        rapport_document = validated_data.pop('rapport_document', None)
        design_document = validated_data.pop('design_document', None)

        # TODO implement file upload to objectstore

        spot = super().create(validated_data)

        if rapport_document:
            Document.objects.create(type=Document.DocumentType.Rapportage,
                                    spot=spot, filename='TODO')
        if design_document:
            Document.objects.create(type=Document.DocumentType.Ontwerp,
                                    spot=spot, filename='TODO')

        return spot

    class Meta(object):
        model = models.Spot
        fields = '__all__'

        # Detail url is constructed using location_id instead of pk,
        # see: https://www.django-rest-framework.org/api-guide/serializers/#how-hyperlinked-views-are-determined # noqa: 501
        extra_kwargs = {
            '_links': {'lookup_field': 'locatie_id'}
        }
