from django.http import HttpResponse, Http404, HttpResponseServerError
import logging
# from rest_framework.decorators import action
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from swiftclient.exceptions import ClientException


from api import serializers
from datapunt_api.rest import DatapuntViewSet

from api.serializers import SpotGeojsonSerializer
from datasets.blackspots import models
# from objectstore_interaction import connection as custom_connection
# from objectstore_interaction import documents

logger = logging.getLogger(__name__)


def get_container_name(document_type: str) -> str:
    if document_type == models.Document.DOCUMENT_TYPE[0][0]:
        return 'doc/ontwerp'
    else:
        return 'doc/rapportage'


class GeojsonRenderer(JSONRenderer):
    """
    Simpy allows for ?format=geojson to be used to get a Json response
    """
    format = 'geojson'


class SpotViewSet(DatapuntViewSet):
    queryset = models.Spot.objects.all().order_by('pk')
    serializer_class = serializers.SpotSerializer
    serializer_detail_class = serializers.SpotSerializer
    lookup_field = 'locatie_id'
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, GeojsonRenderer)

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


def handle_swift_exception(filename: str, e: ClientException) -> HttpResponse:
    """
    Convert swift exception to proper HTTP Response
    Almost all swift client errors are the generic "ClientException".
    The exception message is used to make a better determination of the exception.
    Also note that most connection errors happen on usage of the connection(here),
    instead of the connection setup.
    """
    if 'Unauthorized' in e.msg or 'Authorization Failure' in e.msg:
        logger.error(f'Error with object store connection, error: {e}')
        return HttpResponseServerError()

    if 'Object GET failed' in e.msg:
        logger.error(f'Requested file not found on object store: {filename}, error: {e.msg}')
        raise Http404("File does not exist")

    logger.error(f'Unkown swift client error: {filename}, error: {e.msg}')
    return HttpResponseServerError()


class DocumentViewSet(DatapuntViewSet):
    queryset = models.Document.objects.all().order_by('pk')
    serializer_class = serializers.DocumentSerializer
    serializer_detail_class = serializers.DocumentSerializer

    # TODO reactivate
    # @action(detail=True, url_path='file', methods=['get'])
    # def get_file(self, request, pk=None):
    #     document_model = self.get_object()
    #     container_name = get_container_name(document_model.type)
    #     filename = document_model.filename
    #
    #     connection = custom_connection.get_blackspots_connection()
    #     try:
    #         store_object = documents.get_actual_document(connection, container_name, filename)
    #     except ClientException as e:
    #         return handle_swift_exception(filename, e)
    #
    #     content_type = store_object[0].get('content-type')
    #     obj_data = store_object[1]
    #
    #     response = HttpResponse(content_type=content_type)
    #     response['Content-Disposition'] = f'attachment; filename="{filename}"'
    #     response.write(obj_data)
    #
    #     return response
