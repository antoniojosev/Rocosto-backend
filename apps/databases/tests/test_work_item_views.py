from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from apps.databases.models import Database, Material, Unit, WorkItem
from utils.tests import BaseTestCase

User = get_user_model()


class WorkItemViewSetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.database = Database.objects.create(
            code='DB001',
            name='Test Database',
            description='Test Description',
            user=self.user
        )
        self.unit = Unit.objects.create(
            name='Metro',
            symbol='m'
        )
        self.material = Material.objects.create(
            code='MT001',
            description='Test Material',
            unit=self.unit,
            cost=100.00,
            database=self.database
        )
        self.work_item = WorkItem.objects.create(
            code='WI001',
            description='Test Work Item',
            unit='m',
            yield_rate=1.0,
            database=self.database
        )
        self.url = reverse('workitem-list')
        self.detail_url = reverse(
            'workitem-detail', kwargs={'pk': self.work_item.id})

    def test_create_work_item(self):
        data = {
            'code': 'WI002',
            'description': 'New Work Item',
            'unit': 'm',
            'yield_rate': 2.0,
            'database_id': str(self.database.id),
            'material_ids': [str(self.material.id)]
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkItem.objects.count(), 2)

    def test_create_work_item_invalid_yield_rate(self):
        data = {
            'code': 'WI002',
            'description': 'New Work Item',
            'unit': 'm',
            'yield_rate': -1.0,
            'database_id': str(self.database.id)
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
