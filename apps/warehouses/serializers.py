from rest_framework import serializers
from apps.warehouses.models import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    """Serializer for Warehouse model"""
    manager_name = serializers.CharField(source='manager.full_name', read_only=True, allow_null=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Warehouse
        fields = ['warehouse_id', 'warehouse_name', 'location', 'organization_id',
                  'manager_id', 'manager_name', 'capacity', 'status', 'organization_name',
                  'created_at', 'updated_at']
        read_only_fields = ['warehouse_id', 'created_at', 'updated_at']

