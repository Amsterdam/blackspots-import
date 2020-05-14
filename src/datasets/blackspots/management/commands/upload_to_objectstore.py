from django.conf import settings
from django.core.management.base import BaseCommand

from objectstore import objectstore


class Command(BaseCommand):
    help = "Given a filepath, uploads that file to the Objectstore"

    def add_arguments(self, parser):
        parser.add_argument('filepath', type=str)

    def handle(self, *args, **options):
        file = open(options['filepath'], 'rb')
        file_name = settings.OBJECTSTORE_FILE
        container = settings.OBJECTSTORE_CONTAINER

        conn = objectstore.get_connection(settings.OBJECTSTORE_CONF)

        headers, obj_store_file_list = conn.get_container(container, prefix=file_name)

        if obj_store_file_list and obj_store_file_list[0]['name'] == file_name:
            conn.delete_object(settings.OBJECTSTORE_CONTAINER, file_name)

        conn.put_object(
            settings.OBJECTSTORE_CONTAINER, file_name, contents=file, content_type='text'
        )
