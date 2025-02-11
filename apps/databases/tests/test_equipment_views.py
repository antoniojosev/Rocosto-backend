from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from apps.databases.models import Database, Equipment
from utils.tests import BaseTestCase

User = get_user_model()


class EquipmentViewSetTests(BaseTestCase):
    def setUp(self):
        # pylint: disable=R0801
        super().setUp()
        self.database = Database.objects.create(
            code='DB001',
            name='Test Database',
            description='Test Description',
            user=self.user
        )
        self.equipment = Equipment.objects.create(
            code='EQ001',
            description='Test Equipment',
            cost=100.00,
            depreciation=10.00,
            database=self.database
        )
        self.url = reverse('equipment-list')
        self.detail_url = reverse(
            'equipment-detail', kwargs={'pk': self.equipment.id})

    def test_create_equipment(self):
        data = {
            'code': 'EQ002',
            'description': 'New Equipment',
            'cost': 200.00,
            'depreciation': 20.00,
            'database_id': str(self.database.id)
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Equipment.objects.count(), 2)

    def test_create_equipment_invalid_cost(self):
        data = {
            'code': 'EQ002',
            'description': 'New Equipment',
            'cost': -200.00,
            'depreciation': 20.00,
            'database_id': str(self.database.id)
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
