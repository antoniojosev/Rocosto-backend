from rest_framework import viewsets

from ..models import Database, Equipment, Labor, Material, Unit, WorkItem
from ..serializers.serializers import (
    DatabaseSerializer,
    EquipmentSerializer,
    LaborSerializer,
    MaterialSerializer,
    UnitSerializer,
    WorkItemSerializer,
)

# pylint: disable=too-many-ancestors


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class DatabaseViewSet(viewsets.ModelViewSet):
    queryset = Database.objects.all()
    serializer_class = DatabaseSerializer


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer


class LaborViewSet(viewsets.ModelViewSet):
    queryset = Labor.objects.all()
    serializer_class = LaborSerializer


class WorkItemViewSet(viewsets.ModelViewSet):
    queryset = WorkItem.objects.all()
    serializer_class = WorkItemSerializer
