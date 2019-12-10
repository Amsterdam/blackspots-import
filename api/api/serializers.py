import logging

from datapunt_api.rest import HALSerializer
from django.conf import settings
from django.db import models
from django.db.models import query
from django.utils import six
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from api.bag_geosearch import BagGeoSearchAPI
from datasets.blackspots.models import Document, Spot
from storage.objectstore import ObjectStore

logger = logging.getLogger(__name__)


class DocumentSerializer(HALSerializer):
    spot = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='spot-detail',
        lookup_field='locatie_id',
    )

    class Meta(object):
        model = Document
        fields = '__all__'


class SpotDocumentSerializer(HALSerializer):
    id = serializers.ReadOnlyField()

    class Meta(object):
        model = Document
        exclude = ['spot']


class SpotGeojsonSerializer(GeoFeatureModelSerializer):
    id = serializers.ReadOnlyField()
    stadsdeel = serializers.CharField(source='get_stadsdeel_display', read_only=True)
    documents = SpotDocumentSerializer(many=True, read_only=True)

    class Meta(object):
        model = Spot
        fields = '__all__'
        geo_field = 'point'

        # Detail url is constructed using location_id instead of pk,
        # see: https://www.django-rest-framework.org/api-guide/serializers/#how-hyperlinked-views-are-determined # noqa: 501
        extra_kwargs = {
            '_links': {'lookup_field': 'locatie_id'}
        }


class DisplayChoiceField(serializers.ChoiceField):
    """
    We override the ChoiceField because its to_representation will not return the display value,
    but rather its actual value (which often is a shorthand for the display).
    """

    def to_representation(self, value):
        if value in ('', None):
            return value
        return self.choices.get(six.text_type(value), value)


class SpotSerializer(HALSerializer):
    id = serializers.ReadOnlyField()
    stadsdeel = DisplayChoiceField(choices=Spot.Stadsdelen.choices, required=False)
    documents = SpotDocumentSerializer(many=True, read_only=True)
    rapport_document = serializers.FileField(required=False, allow_null=True)
    design_document = serializers.FileField(required=False, allow_null=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        self.validate_spot_types(attrs)
        self.validate_point_stadsdeel(attrs)

        return attrs

    def validate_spot_types(self, attrs):
        spot_type = attrs.get('spot_type')
        if spot_type in [Spot.SpotType.blackspot, Spot.SpotType.wegvak]:
            if not attrs.get('jaar_blackspotlijst'):
                raise serializers.ValidationError({
                    'jaar_blackspotlijst': [
                        "jaar_blackspotlijst is required for spot types 'blackspot' and 'wegvak'"
                    ]
                })
        else:
            # type is not blackspot or redroute, so we need to make sure jaar_blackspotlijst is empty
            # note that by setting the attribute to None, it will be emptied in the db.
            attrs['jaar_blackspotlijst'] = None

        if spot_type in [Spot.SpotType.protocol_ernstig, Spot.SpotType.protocol_dodelijk]:
            if not attrs.get('jaar_ongeval_quickscan'):
                raise serializers.ValidationError({
                    'jaar_ongeval_quickscan': [
                        "jaar_ongeval_quickscan is required for spot types 'protocol_ernstig' and 'protocol_dodelijk'"
                    ]
                })
        else:
            # type is not protocol_*, so we need to make sure jaar_ongeval_quickscan is empty
            # note that by setting the attribute to None, it will be emptied in the db.
            attrs['jaar_ongeval_quickscan'] = None

    def validate_point_stadsdeel(self, attrs):
        stadsdeel = attrs.get('stadsdeel')
        point = attrs.get('point')
        if point and not stadsdeel:
            # only do a stadsdeel lookup if we did not get it from the request
            stadsdeel = self.determine_stadsdeel(point)
            if stadsdeel == Spot.Stadsdelen.Geen:
                raise serializers.ValidationError({'point': ['Point could not be matched to stadsdeel']})
            elif stadsdeel == Spot.Stadsdelen.BagFout:
                raise serializers.ValidationError({'point': ['Failed to get stadsdeel for point']})
            attrs['stadsdeel'] = stadsdeel

    def determine_stadsdeel(self, point):
        lat = point.y
        lon = point.x
        return BagGeoSearchAPI().get_stadsdeel(lat=lat, lon=lon)

    def create(self, validated_data):
        rapport_file = validated_data.pop('rapport_document', None)
        design_file = validated_data.pop('design_document', None)

        spot = super().create(validated_data)
        self.handle_documents(spot, rapport_file, design_file)
        return spot

    def update(self, instance, validated_data):
        if 'rapport_document' in validated_data and validated_data['rapport_document'] is None:
            # delete rapport_document
            self.delete_document(spot=instance, document_type=Document.DocumentType.Rapportage)

        if 'design_document' in validated_data and validated_data['design_document'] is None:
            # delete design document
            self.delete_document(spot=instance, document_type=Document.DocumentType.Ontwerp)

        rapport_file = validated_data.pop('rapport_document', None)
        design_file = validated_data.pop('design_document', None)

        spot = super().update(instance, validated_data)
        self.handle_documents(spot, rapport_file, design_file)
        return spot

    def delete_document(self, spot, document_type):
        document = Document.objects.filter(spot=spot, type=document_type).first()
        if document:
            objstore = ObjectStore(settings.OBJECTSTORE_CONNECTION_CONFIG)
            objstore.delete(document)
            document.delete()
        else:
            logger.error(f"Delete document was called for spot {spot.locatie_id} and document_type {document_type}, "
                         f"but it does not exist in our database")

    def handle_documents(self, spot, rapport_file=None, design_file=None):
        objstore = ObjectStore(settings.OBJECTSTORE_CONNECTION_CONFIG)
        if rapport_file:
            try:
                rapport_document, created = Document.objects.get_or_create(
                    type=Document.DocumentType.Rapportage, spot=spot)
                objstore.upload(rapport_file, rapport_document)
            except:  # noqa E722 - ignore flake8 check, using bare except
                raise

        if design_file:
            try:
                design_document, created = Document.objects.get_or_create(
                    type=Document.DocumentType.Ontwerp, spot=spot)
                objstore.upload(design_file, design_document)
            except:  # noqa E722 - ignore flake8 check, using bare except
                raise

    class Meta(object):
        model = Spot
        fields = '__all__'

        # Detail url is constructed using location_id instead of pk,
        # see: https://www.django-rest-framework.org/api-guide/serializers/#how-hyperlinked-views-are-determined # noqa: 501
        extra_kwargs = {
            '_links': {'lookup_field': 'locatie_id'}
        }


class GeneratorListSerializer(serializers.ListSerializer):
    """
    Return data as a generator instead of a list
    """

    def to_representation(self, data):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        # Dealing with nested relationships, data can be a Manager,
        # so, get a queryset from the Manager if needed
        # Use an iterator on the queryset to allow large querysets to be
        # exported without excessive memory usage
        if isinstance(data, models.Manager):
            iterable = data.all().iterator()
        elif isinstance(data, query.QuerySet):
            iterable = data.iterator()
        else:
            iterable = data
        # Return a generator rather than a list so that streaming responses
        # can be used
        return (self.child.to_representation(item) for item in iterable)

    @property
    def data(self):
        # Note we deliberately return the super of ListSerializer to avoid
        # instantiating a ReturnList, which would force evaluating the generator
        return super(serializers.ListSerializer, self).data


class SpotCSVSerializer(ModelSerializer):
    stadsdeel = serializers.CharField(source='get_stadsdeel_display')
    type = serializers.CharField(source='spot_type')
    nummer = serializers.CharField(source='locatie_id')
    naam = serializers.CharField(source='description')
    jaar = serializers.SerializerMethodField()
    taken = serializers.CharField(source='tasks')
    aantekeningen = serializers.CharField(source='notes')

    def get_jaar(self, obj):
        if obj.spot_type in [Spot.SpotType.blackspot, Spot.SpotType.wegvak]:
            return obj.jaar_blackspotlijst
        if obj.spot_type in [Spot.SpotType.protocol_dodelijk, Spot.SpotType.protocol_ernstig]:
            return obj.jaar_ongeval_quickscan
        return ''

    class Meta:
        model = Spot
        fields = [
            'stadsdeel',
            'type',
            'nummer',
            'naam',
            'status',
            'start_uitvoering',
            'eind_uitvoering',
            'jaar',
            'taken',
            'aantekeningen'

        ]

        list_serializer_class = GeneratorListSerializer
