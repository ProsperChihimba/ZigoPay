from rest_framework import serializers
from apps.customers.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Customer
        fields = ['customer_id', 'customer_name', 'phone_number', 'email', 
                  'address', 'preferred_communication', 'organization_id',
                  'organization_name', 'created_at', 'updated_at']
        read_only_fields = ['customer_id', 'created_at', 'updated_at']

