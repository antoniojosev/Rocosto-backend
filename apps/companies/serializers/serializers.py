from rest_framework import serializers

from apps.companies.models import Company
from apps.databases.serializers.serializers import UserSerializer


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model"""
    owners = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = (
            'id',
            'tax_id',
            'name',
            'address',
            'phone',
            'owners',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'user')

    def create(self, validated_data):
        """Asigna el usuario actual al crear la compañía"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CompanyPublicSerializer(serializers.ModelSerializer):
    """Serializer for Company model"""

    class Meta:
        model = Company
        fields = (
            'id',
            'name',
        )
