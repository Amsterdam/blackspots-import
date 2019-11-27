import logging

from datapunt_api.rest import DatapuntViewSet
from django.http import Http404, HttpResponse, HttpResponseServerError
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.viewsets import ModelViewSet
from swiftclient.exceptions import ClientException

from api import serializers
from api.renderers import StreamingCSVRenderer, GeojsonRenderer
from api.serializers import SpotGeojsonSerializer
from datasets.blackspots import models
from objectstore_interaction import connection as custom_connection
from objectstore_interaction import documents

logger = logging.getLogger(__name__)


def get_container_name(document_type: str) -> str:
    if document_type == models.Document.DocumentType.Ontwerp:
        return 'doc/ontwerp'
    else:
        return 'doc/rapportage'




class SpotViewSet(DatapuntViewSet, ModelViewSet):
    queryset = models.Spot.objects.all().order_by('pk')
    serializer_class = serializers.SpotSerializer
    serializer_detail_class = serializers.SpotSerializer
    lookup_field = 'locatie_id'
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, GeojsonRenderer)
    parser_classes = [FormParser, MultiPartParser]

    def get_serializer_class(self, *args, **kwargs):
        """
        Overwrites super method to use custom Geosjon serializer based on "format" query param
        """
        if self.request.accepted_renderer.format == 'geojson':
            return SpotGeojsonSerializer
        else:
            return DatapuntViewSet.get_serializer_class(self, *args, **kwargs)

    def paginate_queryset(self, *args, **kwargs):
        """
        Overwrites super method to not use pagination on "format" query param
        """
        if self.request.accepted_renderer.format == 'geojson':
            return None
        else:
            return DatapuntViewSet.paginate_queryset(self, *args, **kwargs)


def handle_swift_exception(container_name: str, filename: str, e: ClientException) -> HttpResponse:
    """
    Convert swift exception to proper HTTP Response
    Almost all swift client errors are the generic "ClientException".
    The exception message is used to make a better determination of the exception.
    Also note that most connection errors happen on usage of the connection(here),
    instead of the connection setup.
    """
    path = f"{container_name}/{filename}"

    if 'Unauthorized' in e.msg or 'Authorization Failure' in e.msg:
        logger.error(f'Error with object store connection, error: {e}')
        return HttpResponseServerError()

    if 'Object GET failed' in e.msg:
        logger.error(f'Requested file not found on object store: {path}, error: {e.msg}')
        raise Http404("File does not exist")

    logger.error(f'Unkown swift client error: {path}, error: {e.msg}')
    return HttpResponseServerError()


class DocumentViewSet(DatapuntViewSet):
    queryset = models.Document.objects.all().order_by('pk')
    serializer_class = serializers.DocumentSerializer
    serializer_detail_class = serializers.DocumentSerializer

    @action(detail=True, url_path='file', methods=['get'])
    def get_file(self, request, pk=None):
        document_model = self.get_object()
        container_name = get_container_name(document_model.type)
        filename = document_model.filename

        connection = custom_connection.get_blackspots_connection()
        try:
            store_object = documents.get_actual_document(connection, container_name, filename)
        except ClientException as e:
            return handle_swift_exception(container_name, filename, e)

        content_type = store_object[0].get('content-type')
        obj_data = store_object[1]

        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(obj_data)

        return response
