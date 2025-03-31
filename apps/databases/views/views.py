from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from ..models import Database, Equipment, Labor, Material, Unit, WorkItem
from ..serializers.serializers import (
    DatabaseResourceStatsSerializer,
    DatabaseSerializer,
    EquipmentSerializer,
    LaborSerializer,
    MaterialSerializer,
    UnitSerializer,
    WorkItemSerializer,
    WorkItemUpdateSerializer,
)

# pylint: disable=too-many-ancestors


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class DatabaseViewSet(viewsets.ModelViewSet):
    queryset = Database.objects.all()
    serializer_class = DatabaseSerializer


class DatabaseResourceStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving database statistics and filtered resources.
    Only supports read operations with optional filtering in retrieve method.
    """
    queryset = Database.objects.all()
    serializer_class = DatabaseResourceStatsSerializer

    VALID_FILTERS = ['MAT', 'EQU', 'LAB', 'WI']

    def get_filter_type(self):
        """
        Gets and validates the filter type from request parameters.
        Returns the filter_type if valid, None otherwise.
        """
        if hasattr(self, '_filter_type_cache'):
            return self._filter_type_cache

        filter_type = self.request.query_params.get('filter')
        print(f"Filter type: {filter_type}")

        if not filter_type:
            self._filter_type_cache = None
            return None

        if filter_type not in self.VALID_FILTERS:
            raise ValidationError(
                f"Invalid filter type: {filter_type}. Valid options are: {', '.join(self.VALID_FILTERS)}"
            )

        self._filter_type_cache = filter_type
        return filter_type

    def get_serializer_context(self):
        """
        Adds resource_type to context when applicable for retrieve operations.
        """
        context = super().get_serializer_context()
        context['is_retrieve'] = self.action == 'retrieve'

        if self.action == 'retrieve':
            try:
                filter_type = self.get_filter_type()
                if filter_type:
                    context['resource_type'] = filter_type
            except ValidationError:
                # Will be handled in retrieve method
                pass

        return context

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a database instance with optional filtering.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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

    def get_serializer_class(self):
        if self.action == 'update':
            return WorkItemUpdateSerializer
        return self.serializer_class

    def update(self, request, *args, **kwargs):
        print("Entrando al método UPDATE de WorkItemViewSet")
        return super().update(request, *args, **kwargs)

    def get_object(self):
        # Asegúrate de que obtienes la instancia de WorkItem correctamente
        return self.queryset.get(id=self.kwargs['pk'])
