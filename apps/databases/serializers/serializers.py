from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

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


class MaterialSerializer(serializers.ModelSerializer):
    unit = UnitSerializer(read_only=True)
    unit_id = serializers.UUIDField(write_only=True)
    database = DatabaseSerializer(read_only=True)
    database_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Material
        fields = ['id', 'code', 'description', 'unit', 'unit_id',
                  'cost', 'database', 'database_id']

    def validate(self, attrs):
        database_id = attrs.get('database_id')
        code = attrs.get('code')

        if self.instance:
            if database_id:
                database = Database.objects.get(id=database_id)
            else:
                database = self.instance.database

            exists = Material.objects.filter(
                code=code,
                database=database
            ).exclude(id=self.instance.id).exists()
        else:
            database = Database.objects.get(id=database_id)
            exists = Material.objects.filter(
                code=code,
                database=database
            ).exists()

        if exists:
            raise serializers.ValidationError({
                'code': 'Ya existe un material con este código en la base de datos.'
            })

        if attrs.get('cost', 0) <= 0:
            raise serializers.ValidationError({
                'cost': 'El costo debe ser mayor que cero.'
            })

        return attrs

    def validate_unit_id(self, value):
        try:
            Unit.objects.get(id=value)
            return value
        except ObjectDoesNotExist as exc:
            raise serializers.ValidationError(
                "La unidad especificada no existe.") from exc


class EquipmentSerializer(serializers.ModelSerializer):
    database = DatabaseSerializer(read_only=True)
    database_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Equipment
        fields = ['id', 'code', 'description', 'cost',
                  'depreciation', 'database', 'database_id']

    def validate_database_id(self, value):
        try:
            Database.objects.get(id=value)
            return value
        except ObjectDoesNotExist as exc:
            raise serializers.ValidationError(
                "La base de datos especificada no existe.") from exc

    def validate(self, attrs):
        database_id = attrs.get('database_id')
        code = attrs.get('code')

        if self.instance:
            if database_id:
                database = Database.objects.get(id=database_id)
            else:
                database = self.instance.database

            exists = Equipment.objects.filter(
                code=code,
                database=database
            ).exclude(id=self.instance.id).exists()
        else:
            database = Database.objects.get(id=database_id)
            exists = Equipment.objects.filter(
                code=code,
                database=database
            ).exists()

        if exists:
            raise serializers.ValidationError({
                'code': 'Ya existe un equipo con este código en la base de datos.'
            })

        if attrs.get('cost', 0) <= 0:
            raise serializers.ValidationError({
                'cost': 'El costo debe ser mayor que cero.'
            })

        if attrs.get('depreciation', 0) <= 0:
            raise serializers.ValidationError({
                'depreciation': 'La depreciación debe ser mayor que cero.'
            })

        return attrs

    def create(self, validated_data):
        database_id = validated_data.pop('database_id')
        database_instance = Database.objects.get(id=database_id)
        equipment = Equipment.objects.create(
            database=database_instance,
            **validated_data
        )
        return equipment

    def update(self, instance, validated_data):
        if 'database_id' in validated_data:
            database_id = validated_data.pop('database_id')
            instance.database = Database.objects.get(id=database_id)
        return super().update(instance, validated_data)


class LaborSerializer(serializers.ModelSerializer):
    database = DatabaseSerializer(read_only=True)
    database_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Labor
        fields = ['id', 'code', 'description', 'hourly_cost',
                  'database', 'database_id']

    def validate(self, attrs):
        database_id = attrs.get('database_id')
        code = attrs.get('code')

        if self.instance:
            if database_id:
                database = Database.objects.get(id=database_id)
            else:
                database = self.instance.database

            exists = Labor.objects.filter(
                code=code,
                database=database
            ).exclude(id=self.instance.id).exists()
        else:
            database = Database.objects.get(id=database_id)
            exists = Labor.objects.filter(
                code=code,
                database=database
            ).exists()

        if exists:
            raise serializers.ValidationError({
                'code': 'Ya existe un recurso de mano de obra con este código.'
            })

        if attrs.get('hourly_cost', 0) <= 0:
            raise serializers.ValidationError({
                'hourly_cost': 'El costo por hora debe ser mayor que cero.'
            })

        return attrs


class WorkItemSerializer(serializers.ModelSerializer):
    materials = MaterialSerializer(many=True, read_only=True)
    equipment = EquipmentSerializer(many=True, read_only=True)
    labor = LaborSerializer(many=True, read_only=True)
    database = DatabaseSerializer(read_only=True)
    database_id = serializers.UUIDField(write_only=True)
    material_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    equipment_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    labor_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = WorkItem
        fields = [
            'id', 'code', 'description', 'unit',
            'materials', 'equipment', 'labor',
            'yield_rate', 'database', 'database_id',
            'material_ids', 'equipment_ids', 'labor_ids'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        database_id = attrs.get('database_id')
        code = attrs.get('code')

        # Validar existencia y unicidad del código
        if self.instance:
            if database_id:
                database = Database.objects.get(id=database_id)
            else:
                database = self.instance.database

            exists = WorkItem.objects.filter(
                code=code,
                database=database
            ).exclude(id=self.instance.id).exists()
        else:
            database = Database.objects.get(id=database_id)
            exists = WorkItem.objects.filter(
                code=code,
                database=database
            ).exists()

        if exists:
            raise serializers.ValidationError({
                'code': 'Ya existe un ítem de trabajo con este código.'
            })

        if attrs.get('yield_rate', 0) <= 0:
            raise serializers.ValidationError({
                'yield_rate': 'El rendimiento debe ser mayor que cero.'
            })

        if 'material_ids' in attrs:
            material_ids = attrs['material_ids']
            materials = Material.objects.filter(
                id__in=material_ids,
                database=database
            )
            if len(materials) != len(material_ids):
                raise serializers.ValidationError({
                    'material_ids': 'Uno o más materiales no existen o no pertenecen a la base de datos.'
                })

        if 'equipment_ids' in attrs:
            equipment_ids = attrs['equipment_ids']
            equipment = Equipment.objects.filter(
                id__in=equipment_ids,
                database=database
            )
            if len(equipment) != len(equipment_ids):
                raise serializers.ValidationError({
                    'equipment_ids': 'Uno o más equipos no existen o no pertenecen a la base de datos.'
                })

        if 'labor_ids' in attrs:
            labor_ids = attrs['labor_ids']
            labor = Labor.objects.filter(
                id__in=labor_ids,
                database=database
            )
            if len(labor) != len(labor_ids):
                raise serializers.ValidationError({
                    'labor_ids': 'Uno o más recursos de mano de obra no existen o no pertenecen a la base de datos.'
                })

        return attrs

    def create(self, validated_data):
        material_ids = validated_data.pop('material_ids', [])
        equipment_ids = validated_data.pop('equipment_ids', [])
        labor_ids = validated_data.pop('labor_ids', [])
        database_id = validated_data.pop('database_id')

        database_instance = Database.objects.get(id=database_id)
        work_item = WorkItem.objects.create(
            database=database_instance,
            **validated_data
        )

        if material_ids:
            work_item.materials.set(material_ids)
        if equipment_ids:
            work_item.equipment.set(equipment_ids)
        if labor_ids:
            work_item.labor.set(labor_ids)

        return work_item

    def update(self, instance, validated_data):
        if 'material_ids' in validated_data:
            instance.materials.set(validated_data.pop('material_ids'))
        if 'equipment_ids' in validated_data:
            instance.equipment.set(validated_data.pop('equipment_ids'))
        if 'labor_ids' in validated_data:
            instance.labor.set(validated_data.pop('labor_ids'))

        if 'database_id' in validated_data:
            database_id = validated_data.pop('database_id')
            instance.database = Database.objects.get(id=database_id)

        return super().update(instance, validated_data)
