import logging
from datetime import date

from datapunt_api.rest import DatapuntViewSet
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseServerError, StreamingHttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from swiftclient.exceptions import ClientException

from api import serializers
from api.renderers import GeojsonRenderer, StreamingCSVRenderer
from api.serializers import SpotCSVSerializer, SpotGeojsonSerializer
from datasets.blackspots import models
from storage.objectstore import ObjectStore

logger = logging.getLogger(__name__)


class SpotViewSet(DatapuntViewSet, ModelViewSet):
    queryset = models.Spot.objects.all().order_by('pk')
    serializer_class = serializers.SpotSerializer
    serializer_detail_class = serializers.SpotSerializer
    lookup_field = 'id'
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


class CSVDownloadViewSet:

    def stream_csv_download(self, stream_response, serializer, filename_prefix):
        renderer = StreamingCSVRenderer()

        # the actual serializer might be wrapped by using list_serializer_class
        actual_serializer = getattr(serializer, 'child') if hasattr(serializer, 'child') else serializer
        fieldnames = actual_serializer.get_fields().keys()

        response_class = StreamingHttpResponse if stream_response else HttpResponse
        response = response_class(renderer.render(data=serializer.data, fieldnames=fieldnames), content_type="text/csv")

        today = date.today()
        filename = f"{filename_prefix}_{today}.csv"
        response['Content-Disposition'] = b'attachment; filename=' + filename.encode(encoding='utf-8') + b';'

        return response


class SpotExportViewSet(mixins.ListModelMixin, GenericViewSet, CSVDownloadViewSet):
    queryset = models.Spot.objects.all().order_by('stadsdeel', 'spot_type', 'pk')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['stadsdeel', 'spot_type', 'status']
    serializer_class = SpotCSVSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return self.stream_csv_download(
            stream_response=True, serializer=serializer, filename_prefix="wba_export")


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
        container_path = ObjectStore.get_container_path(document_model.type)
        filename = document_model.filename

        objstore = ObjectStore(settings.OBJECTSTORE_CONNECTION_CONFIG)
        connection = objstore.get_connection()
        try:
            store_object = objstore.get_document(connection, container_path, filename)
        except ClientException as e:
            return handle_swift_exception(container_path, filename, e)

        content_type = store_object[0].get('content-type')
        obj_data = store_object[1]

        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(obj_data)

        return response
