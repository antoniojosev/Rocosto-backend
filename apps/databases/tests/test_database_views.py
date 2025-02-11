from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from apps.databases.models import Database
from utils.tests import BaseTestCase

User = get_user_model()


class DatabaseViewSetTests(BaseTestCase):
    def setUp(self):
        # pylint: disable=R0801
        super().setUp()
        self.database = Database.objects.create(
            code='DB001',
            name='Test Database',
            description='Test Description',
            user=self.user
        )
        self.url = reverse('database-list')
        self.detail_url = reverse(
            'database-detail', kwargs={'pk': self.database.id})

    def test_list_databases(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_database(self):
        data = {
            'code': 'DB002',
            'name': 'New Database',
            'description': 'New Description'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Database.objects.count(), 2)
