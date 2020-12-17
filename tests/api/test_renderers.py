from unittest import TestCase

from api.renderers import StreamingCSVRenderer


class RenderersTestCase(TestCase):
    fieldnames = ['a', 'b', 'c', 'd']
    data = [
        {'a': '1', 'b': '2', 'c': '3', 'd': '4'},
        {'a': '11', 'b': '12', 'c': '13', 'd': '14'},
        {'a': '21', 'b': '22', 'c': '23', 'd': '24'},
    ]

    def test_streaming_csv_render(self):
        """
        Test and assert that the proper csv is rendered (including header and data rows)
        """
        renderer = StreamingCSVRenderer()
        generator = renderer.render(self.data, self.fieldnames)
        self.assertEqual(next(generator), "a;b;c;d\r\n")
        self.assertEqual(next(generator), "1;2;3;4\r\n")
        self.assertEqual(next(generator), "11;12;13;14\r\n")
        self.assertEqual(next(generator), "21;22;23;24\r\n")
        with self.assertRaises(StopIteration):
            next(generator)

    def test_empty_streaming_csv_render(self):
        """
        Test and assert that only the header is rendered when no data exists
        """
        renderer = StreamingCSVRenderer()
        generator = renderer.render([], self.fieldnames)
        self.assertEqual(next(generator), "a;b;c;d\r\n")
        with self.assertRaises(StopIteration):
            next(generator)
