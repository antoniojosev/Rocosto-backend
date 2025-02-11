from django.urls import reverse
from rest_framework import status

from apps.databases.models import Unit
from utils.tests import BaseTestCase


class UnitViewSetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.unit = Unit.objects.create(
            name='Metro',
            symbol='m'
        )
        self.url = reverse('unit-list')
        self.detail_url = reverse('unit-detail', kwargs={'pk': self.unit.id})

    def test_list_units(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_unit(self):
        data = {
            'name': 'Kilogramo',
            'symbol': 'kg'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Unit.objects.count(), 2)

    def test_retrieve_unit(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Metro')
