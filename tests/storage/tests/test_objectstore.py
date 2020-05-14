from unittest import TestCase, mock
from unittest.mock import Mock, mock_open

from django.test import override_settings
from swiftclient import ClientException, Connection

from datasets.blackspots.models import Document
from storage.objectstore import DOWNLOAD_DIR, WBA_CONTAINER_NAME, XLS_OBJECT_NAME, ObjectStore


class ObjectStoreTestCase(TestCase):

    @mock.patch("storage.objectstore.objectstore.get_connection")
    def test_get_connection(self, mocked_get_connection):
        """
        Test and assert that objecstore.get_connection is called with the given
        config, and that the connection is returned.
        """
        mocked_get_connection.return_value = 'this is the connection'
        objstore = ObjectStore(config='this is the config')
        connection = objstore.get_connection()
        mocked_get_connection.assert_called_with('this is the config')
        self.assertEqual(connection, 'this is the connection')

    @mock.patch("storage.objectstore.objectstore.get_connection")
    @mock.patch("storage.objectstore.ObjectStore.get_container_path")
    def test_upload(self, mocked_get_container_path, mocked_get_connection):
        """
        Test and assert that ObjectStore.connection.put_object is called with the correct arguments
        """
        mocked_get_container_path.return_value = 'container/path/'

        objstore = ObjectStore(config='this is the config')
        connection = Connection()
        connection.put_object = Mock()
        mocked_get_connection.return_value = connection

        file = ('mock', 'file')
        document = Document(filename='doc_file_name.pdf', type=Document.DocumentType.Ontwerp)
        objstore.upload(file, document)
        connection.put_object.assert_called_with('container/path/', 'doc_file_name.pdf', file)

    @mock.patch("storage.objectstore.objectstore.get_connection")
    @mock.patch("storage.objectstore.ObjectStore.get_container_path")
    def test_delete(self, mocked_get_container_path, mocked_get_connection):
        """
        Test and assert that delete_object is called with the correct arguments
        """
        mocked_get_container_path.return_value = 'container/path/'

        objstore = ObjectStore(config='this is the config')
        connection = Connection()
        connection.delete_object = Mock()
        mocked_get_connection.return_value = connection

        document = Document(filename='doc_file_name.pdf', type=Document.DocumentType.Ontwerp)
        objstore.delete(document)
        connection.delete_object.assert_called_with('container/path/', 'doc_file_name.pdf')

    @mock.patch("storage.objectstore.objectstore.get_connection")
    @mock.patch("storage.objectstore.ObjectStore.get_container_path")
    def test_delete_non_existing_file(self, mocked_get_container_path, mocked_get_connection):
        """
        Test and assert that delete_object is called with the correct arguments
        """
        mocked_get_container_path.return_value = 'container/path/'

        objstore = ObjectStore(config='this is the config')
        connection = Connection()
        connection.delete_object = Mock(side_effect=ClientException(''))
        mocked_get_connection.return_value = connection

        document = Document(id=1, filename='doc_file_name.pdf', type=Document.DocumentType.Ontwerp)
        with self.assertLogs(level='INFO') as logs:
            objstore.delete(document)

        connection.delete_object.assert_called_with('container/path/', 'doc_file_name.pdf')
        self.assertIn('INFO:storage.objectstore:Failed to delete object for document id 1', logs.output)

    def test_get_document(self):
        """
        Test and assert that connection.get_object is called with the correct arguments
        """
        connection = Mock()
        container_name = 'container_name_mock'
        object_name = 'object_name_mock'

        objstore = ObjectStore(config='this is the config')
        objstore.get_document(connection, container_name, object_name)
        connection.get_object.assert_called_with(container_name, object_name)

    @mock.patch("storage.objectstore.get_full_container_list")
    def test_get_wba_documents_list(self, mocked_get_full_container_list):
        """
        Test and assert that the correct list of documents is returned
        """
        mocked_get_full_container_list.return_value = [
            {'hash': 'hash1', 'last_modified': '2019-08-26T09:08:55.150810',
             'bytes': 1, 'name': 'ontwerp/filename1.pdf', 'content_type': 'application/pdf'},
            {'hash': 'hash2', 'last_modified': '2019-08-26T09:08:55.150810',
             'bytes': 1, 'name': 'rapport/filename2.pdf', 'content_type': 'application/pdf'},
            {'hash': 'hash3', 'last_modified': '2019-08-26T09:08:55.150810',
             'bytes': 1, 'name': 'ontwerp/filename3.pdf', 'content_type': 'application/pdf'},
        ]

        objstore = ObjectStore(config='this is the config')
        return_value = objstore.get_wba_documents_list(connection=None)

        self.assertEqual(return_value, [
            ('ontwerp', 'filename1.pdf'),
            ('rapport', 'filename2.pdf'),
            ('ontwerp', 'filename3.pdf'),
        ])

    @mock.patch("storage.objectstore.os.makedirs")
    @mock.patch("storage.objectstore.os.path.isfile")
    def test_get_file_cache(self, mocked_isfile, mocked_makedirs):
        connection = Mock()
        container_name = 'container_name_mock'
        object_name = 'object_name_mock'

        mocked_isfile.return_value = True

        objstore = ObjectStore(config='this is the config')
        with self.assertLogs(level='INFO') as logs:
            return_value = objstore.get_file(connection, container_name, object_name)

        mocked_makedirs.assert_called_with(DOWNLOAD_DIR, exist_ok=True)
        self.assertIn('INFO:storage.objectstore:Using cached file: object_name_mock', logs.output)
        self.assertEqual(return_value, f"{DOWNLOAD_DIR}{object_name}")

    @mock.patch("storage.objectstore.os.makedirs")
    @mock.patch("storage.objectstore.os.path.isfile")
    @mock.patch("builtins.open", new_callable=mock_open)
    def test_get_file_download(self, mocked_file, mocked_isfile, mocked_makedirs):
        connection = Mock()
        connection.get_object.return_value = [None, 'mocked_data']
        container_name = 'container_name_mock'
        object_name = 'object_name_mock'

        mocked_isfile.return_value = False

        objstore = ObjectStore(config='this is the config')
        with self.assertLogs(level='INFO') as logs:
            return_value = objstore.get_file(connection, container_name, object_name)

        mocked_makedirs.assert_called_with(DOWNLOAD_DIR, exist_ok=True)
        self.assertNotIn('INFO:storage.objectstore:Using cached file: object_name_mock', logs.output)
        connection.get_object.assert_called_with(container_name, object_name)
        mocked_file().write.assert_called_with('mocked_data')
        self.assertEqual(return_value, f"{DOWNLOAD_DIR}{object_name}")

    @mock.patch("storage.objectstore.ObjectStore.get_file")
    def test_fetch_spots(self, mocked_get_file):
        objstore = ObjectStore(config='this is the config')
        objstore.fetch_spots(connection='test connection')
        mocked_get_file.assert_called_with('test connection', WBA_CONTAINER_NAME, XLS_OBJECT_NAME)

    @override_settings(OBJECTSTORE_UPLOAD_CONTAINER_NAME="upload_container_name")
    def test_get_container_path_ontwerp(self):
        """
        Test and assert that the correct container path is returned for type ontwerp
        """
        self.assertEqual(ObjectStore.get_container_path(Document.DocumentType.Ontwerp),
                         f"upload_container_name/doc/ontwerp")

    @override_settings(OBJECTSTORE_UPLOAD_CONTAINER_NAME="upload_container_name")
    def test_get_container_path_rapport(self):
        """
        Test and assert that the correct container path is returned for type rapport
        """
        self.assertEqual(ObjectStore.get_container_path(Document.DocumentType.Rapportage),
                         f"upload_container_name/doc/rapportage")
