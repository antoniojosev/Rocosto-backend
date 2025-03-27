import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.budgets.models import Bond, Budget, Retention
from apps.companies.models import Company
from apps.companies.serializers.serializers import CompanyPublicSerializer
from apps.databases.serializers.serializers import UserSerializer, WorkItemSerializer

User = get_user_model()


class BondSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bond
        fields = [
            'id',
            'title',
            'amount',
            'salary_limit_per_day'
        ]


class RetentionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retention
        fields = [
            'id',
            'retention_type',
            'amount',
            'percentage'
        ]


class BudgetSerializer(serializers.ModelSerializer):
    bonds = BondSerializer(many=True, required=False)
    retentions = RetentionSerializer(many=True, required=False)
    work_item = WorkItemSerializer(many=True, required=False)
    company = CompanyPublicSerializer(many=False)

    class Meta:
        model = Budget
        fields = [
            'id',
            'code',
            'contract',
            'budget_date',
            'name',
            'owner',
            'calculated_by',
            'reviewed_by',
            'hours_per_day',
            'currency',
            'use_associated_cost_factor',
            'direct_labor_factor',
            'iva_type',
            'iva_percentage',
            'administration_percentage',
            'utility_percentage',
            'financing_percentage',
            'use_medical_insurance',
            'bonds',
            'retentions',
            'work_item',
            'created_at',
            'state',
            'company',
        ]
        read_only_fields = ['user']

    def create(self, validated_data):
        bonds_data = validated_data.pop('bonds', [])
        retentions_data = validated_data.pop('retentions', [])

        # Add the current user to the budget
        validated_data['user'] = self.context['request'].user
        budget = Budget.objects.create(**validated_data)

        # Create bonds
        for bond_data in bonds_data:
            Bond.objects.create(budget=budget, **bond_data)

        # Create retentions
        for retention_data in retentions_data:
            Retention.objects.create(budget=budget, **retention_data)

        return budget

    def update(self, instance, validated_data):
        bonds_data = validated_data.pop('bonds', [])
        retentions_data = validated_data.pop('retentions', [])

        # Update budget fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update bonds
        instance.bonds.all().delete()
        for bond_data in bonds_data:
            Bond.objects.create(budget=instance, **bond_data)

        # Update retentions
        instance.retentions.all().delete()
        for retention_data in retentions_data:
            Retention.objects.create(budget=instance, **retention_data)

        return instance


class BudgetCreateSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(write_only=True)
    owner_id = serializers.UUIDField(write_only=True)
    calculated_by_id = serializers.UUIDField(write_only=True)
    reviewed_by_id = serializers.UUIDField(write_only=True)
    company = CompanyPublicSerializer(many=False, read_only=True)
    owner = UserSerializer(many=False, read_only=True)
    calculated_by = UserSerializer(many=False, read_only=True)
    reviewed_by = UserSerializer(many=False, read_only=True)
    work_item = WorkItemSerializer(many=True, read_only=True)
    bonds = BondSerializer(many=True, read_only=True)
    retentions = RetentionSerializer(many=True, read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id',
            'code',
            'name',
            'owner_id',
            'calculated_by_id',
            'reviewed_by_id',
            'direct_labor_factor',
            'iva_type',
            'iva_percentage',
            'administration_percentage',
            'utility_percentage',
            'financing_percentage',
            'use_medical_insurance',
            'company_id',
            'contract',
            'budget_date',
            'owner',
            'calculated_by',
            'reviewed_by',
            'hours_per_day',
            'currency',
            'use_associated_cost_factor',
            'bonds',
            'retentions',
            'work_item',
            'created_at',
            'state',
            'company',
        ]
        read_only_fields = [
            'contract',
            'budget_date',
            'owner',
            'calculated_by',
            'reviewed_by',
            'hours_per_day',
            'currency',
            'use_associated_cost_factor',
            'bonds',
            'retentions',
            'work_item',
            'created_at',
            'state',
            'company',
        ]

    def validate_company_id(self, value):
        if not Company.objects.filter(id=value).exists():
            raise serializers.ValidationError("Company does not exist.")
        return value

    def validate_owner_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Owner does not exist.")
        return value

    def validate_calculated_by_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Calculated by user does not exist.")
        return value

    def validate_reviewed_by_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Reviewed by user does not exist.")
        return value

    def validate(self, data):
        # Check if the company is associated with the user
        user = self.context['request'].user
        company_id = data.get('company_id')
        if not Company.objects.filter(id=company_id, user=user).exists():
            raise serializers.ValidationError(
                "You do not have permission to create a budget for this company.")
        return data

    def create(self, validated_data):

        # Add the current user to the budget
        validated_data['user'] = self.context['request'].user
        validated_data['company'] = Company.objects.get(
            id=validated_data.pop('company_id'))
        validated_data['owner'] = User.objects.get(
            id=validated_data.pop('owner_id'))
        validated_data['calculated_by'] = User.objects.get(
            id=validated_data.pop('calculated_by_id'))
        validated_data['reviewed_by'] = User.objects.get(
            id=validated_data.pop('reviewed_by_id'))
        validated_data['budget_date'] = datetime.date.today()
        budget = Budget.objects.create(**validated_data)

        return budget
