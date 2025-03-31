from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.budgets.models import Budget

from ..models import Database, Equipment, Labor, Material, Unit, WorkItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email']


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'symbol']


class DatabaseSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Database
        fields = ['id', 'code', 'name', 'description', 'user']


class DatabaseCountsSerializer(DatabaseSerializer):
    total_materials = serializers.SerializerMethodField()
    total_equipment = serializers.SerializerMethodField()
    total_labor = serializers.SerializerMethodField()

    class Meta:
        model = Database
        fields = ['id', 'code', 'name', 'description', 'user',
                  'total_materials', 'total_equipment', 'total_labor']

    def get_total_materials(self, obj):
        return obj.materials.count()

    def get_total_equipment(self, obj):
        return obj.equipment.count()

    def get_total_labor(self, obj):
        return obj.labor.count()


class DatabaseWithResourcesSerializer(serializers.ModelSerializer):
    resources = serializers.SerializerMethodField()

    class Meta:
        model = Database
        fields = '__all__'

    def get_resources(self, obj):
        resource_type = self.context.get('resource_type')
        if resource_type == 'MAT':
            materials = Material.objects.filter(database=obj)
            return MaterialSerializer(materials, many=True).data
        elif resource_type == 'EQU':
            equipments = Equipment.objects.filter(database=obj)
            return EquipmentSerializer(equipments, many=True).data
        elif resource_type == 'LAB':
            labors = Labor.objects.filter(database=obj)
            return LaborSerializer(labors, many=True).data
        return None


class DatabaseWithResources1Serializer(DatabaseCountsSerializer):
    data = serializers.SerializerMethodField()

    class Meta:
        model = Database
        fields = ['id', 'code', 'name', 'description', 'user',
                  'total_materials', 'total_equipment', 'total_labor', 'data']

    def get_data(self, obj):
        request = self.context.get('request')
        resource_type = request.query_params.get(
            'resource_type', None) if request else None

        if not resource_type:
            return []

        if resource_type == 'material':
            return MaterialSerializer(obj.material_set.all(), many=True).data
        elif resource_type == 'equipment':
            return EquipmentSerializer(obj.equipment_set.all(), many=True).data
        elif resource_type == 'labor':
            return LaborSerializer(obj.labor_set.all(), many=True).data

        return []


class DatabaseResourceStatsSerializer(DatabaseCountsSerializer):
    """
    Serializer that handles both listing databases with counts and
    retrieving a single database with paginated resources.
    """
    resources = serializers.SerializerMethodField()

    class Meta:
        model = Database
        fields = ['id', 'code', 'name', 'description', 'user',
                  'total_materials', 'total_equipment', 'total_labor', 'resources']

    def get_resources(self, obj):
        # Only include resources in retrieve operations, not in list
        if not self.context.get('is_retrieve', False):
            return None

        resource_type = self.context.get('resource_type')
        if not resource_type:
            return None

        # Get pagination parameters from request
        request = self.context.get('request')
        page_size = request.query_params.get('page_size', 10)
        page = request.query_params.get('page', 1)

        try:
            page_size = int(page_size)
            page = int(page)
        except ValueError:
            page_size = 10
            page = 1

        # Calculate start and end indices for manual pagination
        start = (page - 1) * page_size
        end = start + page_size

        # Get the appropriate resources based on resource_type
        if resource_type == 'MAT':
            queryset = Material.objects.filter(database=obj)
            total = queryset.count()
            materials = queryset[start:end]
            items = MaterialSerializer(materials, many=True).data
        elif resource_type == 'EQU':
            queryset = Equipment.objects.filter(database=obj)
            total = queryset.count()
            equipments = queryset[start:end]
            items = EquipmentSerializer(equipments, many=True).data
        elif resource_type == 'LAB':
            queryset = Labor.objects.filter(database=obj)
            total = queryset.count()
            labors = queryset[start:end]
            items = LaborSerializer(labors, many=True).data
        elif resource_type == 'WI':
            queryset = WorkItem.objects.filter(database=obj)
            total = queryset.count()
            work_items = queryset[start:end]
            items = WorkItemSerializer(work_items, many=True).data
        else:
            return None

        # Return paginated result format
        return {
            'count': total,
            'next': page < (total // page_size) + (1 if total % page_size > 0 else 0),
            'previous': page > 1,
            'results': items
        }


class BaseResourceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    database = DatabaseSerializer(many=False, read_only=True)

    class Meta:
        abstract = True  # Indicamos que es una clase abstracta

    def _get_database(self):
        return self.context.get('database') or Database.objects.first()

    def validate_code(self, value):
        request = self.context.get('request')
        if request and request.method == 'PUT' or self.instance:
            print('oooooooooooooooooooooooooooooooooooooooooooooooooooo')
            return value
        database = self._get_database()
        # Suponiendo que cada serializer derive de un modelo distinto
        model_class = self.Meta.model
        if model_class.objects.filter(code=value, database=database).exists():
            raise serializers.ValidationError(
                'Ya existe un recurso con este código en la base de datos.'
            )
        return value


class MaterialSerializer(BaseResourceSerializer):
    unit = UnitSerializer(many=False, read_only=True)
    unit_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Material
        fields = [
            'id',
            'code',
            'description',
            'unit',
            'unit_id',
            'cost',
            'database',
        ]

    def validate_cost(self, value):
        if self.instance:
            return value
        if value <= 0:
            raise serializers.ValidationError(
                'El costo debe ser mayor que cero.'
            )
        return value

    def validate_unit_id(self, value):
        try:
            Unit.objects.get(id=value)
            return value
        except ObjectDoesNotExist as exc:
            raise serializers.ValidationError(
                "La unidad especificada no existe.") from exc

    def create(self, validated_data):
        unit_id = validated_data.pop('unit_id', None)
        unit = Unit.objects.get(id=unit_id)
        database_instance = self._get_database()
        material = Material.objects.create(
            database=database_instance,
            unit=unit,
            **validated_data
        )
        return material

    def update(self, instance, validated_data):
        unit_id = validated_data.pop('unit_id', None)
        if unit_id:
            instance.unit = Unit.objects.get(id=unit_id)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EquipmentSerializer(BaseResourceSerializer):

    class Meta:
        model = Equipment
        fields = [
            'id',
            'code',
            'description',
            'cost',
            'depreciation',
            'database',
        ]

    def validate_cost(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'El costo debe ser mayor que cero.'
            )
        return value

    def validate_depreciation(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'La depreciación debe ser mayor que cero.'
            )
        return value

    def create(self, validated_data):
        database_instance = self._get_database()
        print('aaaaaaaaaaaa', database_instance)
        equipment = Equipment.objects.create(
            database=database_instance,
            **validated_data
        )
        return equipment

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class LaborSerializer(BaseResourceSerializer):

    class Meta:
        model = Labor
        fields = [
            'id',
            'code',
            'description',
            'hourly_cost',
            'database',
        ]
        read_only_fields = [
            'database',
        ]

    def validate_hourly_cost(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'El costo por hora debe ser mayor que cero.'
            )
        return value

    def create(self, validated_data):
        database_instance = self._get_database()
        labor = Labor.objects.create(
            database=database_instance,
            **validated_data
        )
        return labor

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class WorkItemSerializer(BaseResourceSerializer):

    material = MaterialSerializer(many=True, required=False)
    equipment = EquipmentSerializer(many=True, required=False)
    labor = LaborSerializer(many=True, required=False)
    budget_id = serializers.UUIDField(
        format='hex_verbose', write_only=True, required=True)
    total_labor_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_total_labor_cost')
    total_equipment_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_total_equipment_cost')
    total_material_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_total_material_cost')
    total_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_total_cost')

    class Meta:
        model = WorkItem
        fields = [
            'id',
            'code',
            'description',
            'unit',
            'material',
            'equipment',
            'labor',
            'yield_rate',
            'database',
            'total_labor_cost',
            'total_equipment_cost',
            'total_material_cost',
            'total_cost',
            'covening_code',
            'material_unit_usage',
            'budget_id'

        ]
        read_only_fields = ['id', 'database']

    def validate_budget_id(self, value):
        if self.instance:
            return value
        if not Budget.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                'El presupuesto no existe.'
            )
        return value

    def validate_yield_rate(self, value):
        if self.instance:
            return value
        if value <= 0:
            raise serializers.ValidationError(
                'El rendimiento debe ser mayor que cero.'
            )
        return value

    def _validate_resource_exists(self, resource_id, model_class, resource_name):
        if self.instance:
            return
        try:
            return model_class.objects.get(id=resource_id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({
                resource_name: f'El {resource_name} con id {resource_id} no existe.'
            })

    def _save_resources(self, serializer_class, data, model_class, existing_ids):
        resources = []

        if data:
            serializer = serializer_class(many=True, data=data)
            if serializer.is_valid(raise_exception=True):
                resources.extend(serializer.save())

        if existing_ids:
            resources.extend(model_class.objects.filter(id__in=existing_ids))

        return resources

    def validate(self, attrs):
        # Si estamos actualizando (instance existe), verificar que los recursos pertenezcan al workitem
        if self.instance:
            resource_validations = [
                (attrs.get('material', []), self.instance.material, 'material'),
                (attrs.get('equipment', []), self.instance.equipment, 'equipo'),
                (attrs.get('labor', []), self.instance.labor, 'mano de obra')
            ]

            for resource_data, resource_queryset, resource_name in resource_validations:
                existing_ids = [item['id']
                                for item in resource_data if 'id' in item]
                if existing_ids:
                    valid_ids = set(
                        resource_queryset.values_list('id', flat=True))
                    invalid_ids = set(existing_ids) - valid_ids
                    if invalid_ids:
                        raise serializers.ValidationError({
                            resource_name: (
                                f'Los siguientes IDs de {resource_name} no están relacionados con este item: {invalid_ids}')
                        })

            return super().validate(attrs)

        resource_validations = [
            (attrs.get('material', []), Material, 'material'),
            (attrs.get('equipment', []), Equipment, 'equipo'),
            (attrs.get('labor', []), Labor, 'mano de obra')
        ]

        for resource_data, model_class, resource_name in resource_validations:
            for item in resource_data:
                if 'id' in item:
                    self._validate_resource_exists(
                        item['id'],
                        model_class,
                        resource_name
                    )

        return attrs

    def _process_resource_data(self, resource_data, model_class, resource_name):
        existing_ids = []
        to_create = []

        for item in resource_data:
            if 'id' in item:
                existing_ids.append(item['id'])
            else:
                to_create.append(item)

        return existing_ids, to_create

    def create(self, validated_data):
        # TODO: use transactions
        materials_data = validated_data.pop('material', [])
        equipment_data = validated_data.pop('equipment', [])
        labor_data = validated_data.pop('labor', [])
        budget_id = validated_data.pop('budget_id', [])

        print('xxxxxxxxxxxxxxxxxxxx', self._get_database())

        work_item = WorkItem.objects.create(
            database=self._get_database(),
            **validated_data
        )

        resource_mappings = [
            (materials_data, MaterialSerializer, Material, 'material'),
            (equipment_data, EquipmentSerializer, Equipment, 'equipo'),
            (labor_data, LaborSerializer, Labor, 'mano de obra')
        ]

        for resource_data, serializer_class, model_class, resource_name in resource_mappings:
            existing_ids, to_create = self._process_resource_data(
                resource_data,
                model_class,
                resource_name
            )
            resources = self._save_resources(
                serializer_class, to_create, model_class, existing_ids)

            getattr(work_item, model_class.__name__.lower()).add(*resources)

        Budget.objects.get(id=budget_id).work_item.add(work_item)

        return work_item

    def _update_existing_resources(self, data, serializer_class, model_class):
        updated_resources = []
        for item in data:
            if 'id' in item:
                resource = model_class.objects.get(id=item['id'])
                serializer = serializer_class(
                    resource, data=item, partial=True)
                if serializer.is_valid(raise_exception=True):
                    updated_resources.append(serializer.save())
        return updated_resources

    def update(self, instance, validated_data):
        materials_data = validated_data.pop('material', [])
        equipment_data = validated_data.pop('equipment', [])
        labor_data = validated_data.pop('labor', [])

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Process each resource type
        resource_mappings = [
            (materials_data, MaterialSerializer, Material, instance.material),
            (equipment_data, EquipmentSerializer, Equipment, instance.equipment),
            (labor_data, LaborSerializer, Labor, instance.labor)
        ]

        for data, serializer_class, model_class, relation in resource_mappings:
            if not data:
                continue

            # Update existing resources using serializers
            self._update_existing_resources(
                data,
                serializer_class,
                model_class
            )

            # Handle new resources
            to_create = [item for item in data if 'id' not in item]
            if to_create:
                create_serializer = serializer_class(
                    data=to_create,
                    many=True,
                    context=self.context
                )
                if create_serializer.is_valid(raise_exception=True):
                    new_resources = create_serializer.save()
                    # Solo añadimos los nuevos recursos a la relación
                    relation.add(*new_resources)

        return instance


class WorkItemUpdateSerializer(BaseResourceSerializer):

    material = MaterialSerializer(many=True, required=False)
    equipment = EquipmentSerializer(many=True, required=False)
    labor = LaborSerializer(many=True, required=False)
    total_labor_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_total_labor_cost')
    total_equipment_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_total_equipment_cost')
    total_material_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_total_material_cost')
    total_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_total_cost')

    class Meta:
        model = WorkItem
        fields = [
            'id',
            'code',
            'description',
            'unit',
            'material',
            'equipment',
            'labor',
            'yield_rate',
            'database',
            'total_labor_cost',
            'total_equipment_cost',
            'total_material_cost',
            'total_cost',
            'covening_code',
            'material_unit_usage',

        ]
        read_only_fields = [
            'id',
            'database',
            'description',
            'unit',
            'yield_rate',
            'covening_code',
            'material_unit_usage',
        ]

    def _validate_resource_exists(self, resource_id, model_class, resource_name):
        if self.instance:
            return
        try:
            return model_class.objects.get(id=resource_id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({
                resource_name: f'El {resource_name} con id {resource_id} no existe.'
            })

    def _save_resources(self, serializer_class, data, model_class, existing_ids):
        resources = []

        if data:
            serializer = serializer_class(many=True, data=data)
            if serializer.is_valid(raise_exception=True):
                resources.extend(serializer.save())

        if existing_ids:
            resources.extend(model_class.objects.filter(id__in=existing_ids))

        return resources

    def validate(self, attrs):
        # Si estamos actualizando (instance existe), verificar que los recursos pertenezcan al workitem
        if self.instance:
            resource_validations = [
                (attrs.get('material', []), self.instance.material, 'material'),
                (attrs.get('equipment', []), self.instance.equipment, 'equipo'),
                (attrs.get('labor', []), self.instance.labor, 'mano de obra')
            ]

            for resource_data, resource_queryset, resource_name in resource_validations:
                existing_ids = [item['id']
                                for item in resource_data if 'id' in item]
                if existing_ids:
                    valid_ids = set(
                        resource_queryset.values_list('id', flat=True))
                    invalid_ids = set(existing_ids) - valid_ids
                    if invalid_ids:
                        raise serializers.ValidationError({
                            resource_name: f'Los siguientes IDs de {resource_name} no están relacionados con este item: {invalid_ids}'
                        })
        return attrs

    def _process_resource_data(self, resource_data, model_class, resource_name):
        existing_ids = []
        to_create = []

        for item in resource_data:
            if 'id' in item:
                existing_ids.append(item['id'])
            else:
                to_create.append(item)

        return existing_ids, to_create

    def _update_existing_resources(self, data, serializer_class, model_class):
        updated_resources = []
        for item in data:

            if 'id' in item:
                resource = model_class.objects.get(id=item['id'])
                serializer = serializer_class(
                    instance=resource, data=item, partial=True)
                if serializer.is_valid(raise_exception=True):
                    updated_resources.append(serializer.save())
        return updated_resources

    def update(self, instance, validated_data):
        materials_data = validated_data.pop('material', [])
        equipment_data = validated_data.pop('equipment', [])
        labor_data = validated_data.pop('labor', [])

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # # Process each resource type
        resource_mappings = [
            (materials_data, MaterialSerializer, Material, instance.material),
            (equipment_data, EquipmentSerializer, Equipment, instance.equipment),
            (labor_data, LaborSerializer, Labor, instance.labor)
        ]

        for data, serializer_class, model_class, relation in resource_mappings:
            if not data:
                continue

        #     # Update existing resources using serializers
            self._update_existing_resources(
                data,
                serializer_class,
                model_class
            )

        #     # Handle new resources
            to_create = [item for item in data if 'id' not in item]
            if to_create:

                create_serializer = serializer_class(
                    data=to_create,
                    many=True,
                    context=self.context
                )
                if create_serializer.is_valid(raise_exception=True):
                    new_resources = create_serializer.save()
                    # Solo añadimos los nuevos recursos a la relación
                    relation.add(*new_resources)

        return instance
