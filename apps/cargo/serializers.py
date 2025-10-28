from rest_framework import serializers
from apps.cargo.models import Cargo, CargoHistory


class CargoSerializer(serializers.ModelSerializer):
    """Serializer for Cargo model"""
    customer_name = serializers.CharField(source='customer.customer_name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.warehouse_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Cargo
        fields = ['cargo_id', 'tracking_number', 'customer_id', 'customer_name',
                  'warehouse_id', 'warehouse_name', 'cargo_name', 'description',
                  'origin_location', 'destination_location', 'cargo_weight', 'cargo_value',
                  'container_id', 'origin_tracking_number', 'cbm', 'width', 'height',
                  'length', 'status', 'created_by_id', 'created_by_name',
                  'created_at', 'updated_at']
        read_only_fields = ['cargo_id', 'tracking_number', 'created_at', 'updated_at']


class CargoHistorySerializer(serializers.ModelSerializer):
    """Serializer for Cargo History"""
    updated_by_name = serializers.CharField(source='updated_by.full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = CargoHistory
        fields = ['history_id', 'cargo_id', 'previous_status', 'new_status',
                  'updated_by_id', 'updated_by_name', 'remarks', 'updated_at']
        read_only_fields = ['history_id', 'updated_at']