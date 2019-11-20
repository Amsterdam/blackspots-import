from unittest import TestCase

import pytest
from django.test import Client


class TestViews(TestCase):
    def setUp(self):
        self.http_client = Client()

    @pytest.mark.django_db
    def test_health_view(self):
        response = self.http_client.get('/status/health')
        assert response.status_code == 200
        assert response.content == b"Connectivity OK"
